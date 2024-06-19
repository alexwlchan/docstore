import datetime
import hashlib
import json
import os
import pathlib
import shutil

import cattr

from docstore.file_normalisation import normalised_filename_copy
from docstore.models import (
    DocstoreEncoder,
    Document,
    File,
    Thumbnail,
    from_json,
    to_json,
)
from docstore.text_utils import slugify
from docstore.thumbnails import create_thumbnail, get_dimensions
from docstore.tint_colors import choose_tint_color


def db_path(root: pathlib.Path) -> pathlib.Path:
    """
    Returns the path to the database.
    """
    return root / "documents.json"


_cached_documents = {
    "last_modified": None,
    "contents": None,
}


def read_documents(root: pathlib.Path) -> list[Document]:
    """
    Get a list of all the documents.
    """
    # JSON parsing is somewhat expensive.  By caching the result rather than
    # going to disk each time, we see a ~10x speedup in returning responses
    # from the server.
    try:
        if (
            _cached_documents["last_modified"] is not None
            and os.stat(db_path(root)).st_mtime <= _cached_documents["last_modified"]
        ):
            return _cached_documents["contents"]
    except FileNotFoundError:
        pass

    try:
        with open(db_path(root)) as infile:
            result = from_json(infile.read())
    except FileNotFoundError:
        return []

    _cached_documents["last_modified"] = os.stat(db_path(root)).st_mtime
    _cached_documents["contents"] = result

    return result


def write_documents(*, root: pathlib.Path, documents: list[Document]) -> None:
    json_string = to_json(documents)

    os.makedirs(root, exist_ok=True)

    with open(db_path(root), "w") as out_file:
        out_file.write(json_string)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as infile:
        for byte_block in iter(lambda: infile.read(4096), b""):
            h.update(byte_block)

    return "sha256:%s" % h.hexdigest()


def store_new_document(
    *,
    root: pathlib.Path,
    path: pathlib.Path,
    title: str,
    tags: list[str],
    source_url: str | None,
    date_saved: datetime.datetime,
) -> Document:
    filename = os.path.basename(path)

    # Files are sharded by the first letter of their filename,
    # e.g. "aardvark.png" is saved in "a/aardvark.png"
    shard = slugify(filename)[0].lower()

    dst = os.path.join(root, "files", shard, filename)

    out_path = normalised_filename_copy(src=path, dst=dst)

    thumbnail_path = create_thumbnail(out_path)
    thumbnail_name = os.path.basename(thumbnail_path)
    thumb_out_path = os.path.join(root, "thumbnails", thumbnail_name[0], thumbnail_name)
    os.makedirs(os.path.dirname(thumb_out_path), exist_ok=True)
    shutil.move(thumbnail_path, thumb_out_path)

    tint_color = choose_tint_color(thumbnail_path=thumb_out_path, file_path=out_path)

    hex_tint_color = "#%02x%02x%02x" % tuple(
        int(component * 255) for component in tint_color
    )

    new_document = Document(
        title=title,
        date_saved=date_saved,
        tags=tags,
        files=[
            File(
                filename=filename,
                path=os.path.relpath(out_path, root),
                size=os.stat(out_path).st_size,
                checksum=sha256(out_path),
                source_url=source_url,
                thumbnail=Thumbnail(
                    path=os.path.relpath(thumb_out_path, root),
                    dimensions=get_dimensions(thumb_out_path),
                    tint_color=hex_tint_color,
                ),
                date_saved=date_saved,
            )
        ],
    )

    documents = read_documents(root)
    documents.append(new_document)

    write_documents(root=root, documents=documents)

    # Don't delete the original file until it's been successfully recorded
    # and a thumbnail created.
    os.unlink(path)

    return new_document


def pairwise_merge_documents(
    root: pathlib.Path,
    *,
    doc1: Document,
    doc2: Document,
    new_title: str,
    new_tags: list[str],
) -> Document:
    """
    Merge the files on two documents together.

    Before: 2 documents with 1 file each
    After:  1 document with 2 files
    """
    documents = read_documents(root)
    assert doc2 in documents
    documents.remove(doc2)

    # Modify the copy of the document that's about to be written; this will
    # throw an error if the document has changed between starting and finishing
    # the merge.
    stored_doc1 = documents[documents.index(doc1)]

    stored_doc1.date_saved = min([stored_doc1.date_saved, doc2.date_saved])
    stored_doc1.tags = new_tags
    stored_doc1.title = new_title
    stored_doc1.files.extend(doc2.files)
    write_documents(root=root, documents=documents)

    return stored_doc1


def delete_document(root: pathlib.Path, *, doc_id: str) -> None:
    documents = read_documents(root)
    doc = [d for d in documents if d.id == doc_id][0]

    delete_dir = os.path.join(root, "deleted", doc.id)
    os.makedirs(delete_dir, exist_ok=True)

    for f in doc.files:
        os.rename(
            os.path.join(root, f.path),
            os.path.join(delete_dir, os.path.basename(f.path)),
        )
        os.unlink(os.path.join(root, f.thumbnail.path))

    with open(os.path.join(delete_dir, "document.json"), "w") as outfile:
        outfile.write(
            json.dumps(
                cattr.unstructure(doc), indent=2, sort_keys=True, cls=DocstoreEncoder
            )
        )

    documents = [d for d in documents if d.id != doc_id]
    write_documents(root=root, documents=documents)


def find_original_filename(root, *, path):
    """
    Returns the name of the original file stored in this path.
    """
    documents = read_documents(root)
    for d in documents:
        for f in d.files:
            if f.path == os.path.relpath(path, root):
                return f.filename

    raise ValueError(f"Couldn't find file stored with path {path}")
