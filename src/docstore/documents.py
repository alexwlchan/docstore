import hashlib
import os
import secrets
import shutil

from docstore.models import Document, File, Thumbnail, from_json, to_json
from docstore.text_utils import slugify
from docstore.thumbnails import create_thumbnail


_cached_documents = {
    "last_modified": None,
    "contents": None,
}


def read_documents(root):
    """
    Get a list of all the documents.
    """
    db_path = os.path.join(root, "documents.json")

    # JSON parsing is somewhat expensive.  By caching the result rather than
    # going to disk each time, we see a ~10x speedup in returning responses
    # from the server.
    try:
        if (
            _cached_documents["last_modified"] is not None
            and os.stat(db_path).st_mtime <= _cached_documents["last_modified"]
        ):
            return _cached_documents["contents"]
    except FileNotFoundError:
        pass

    try:
        with open(db_path) as infile:
            result = from_json(infile.read())
    except FileNotFoundError:
        return []

    _cached_documents["last_modified"] = os.stat(db_path).st_mtime
    _cached_documents["contents"] = result

    return result


def write_documents(*, root, documents):
    db_path = os.path.join(root, "documents.json")
    json_string = to_json(documents)

    os.makedirs(root, exist_ok=True)

    with open(db_path, "w") as out_file:
        out_file.write(json_string)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as infile:
        for byte_block in iter(lambda: infile.read(4096), b""):
            h.update(byte_block)

    return "sha256:%s" % h.hexdigest()


def store_new_document(*, root, path, title, tags, source_url, date_saved):
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    slug = slugify(name) + ext

    out_path = os.path.join(root, "files", slug[0], slug)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    while os.path.exists(out_path):
        out_path = os.path.join(
            root, "files", slug[0], slugify(name) + "_" + secrets.token_hex(2) + ext
        )

    shutil.move(path, out_path)

    thumbnail_path = create_thumbnail(out_path)
    thumbnail_name = os.path.basename(thumbnail_path)
    thumb_out_path = os.path.join(root, "thumbnails", thumbnail_name[0], thumbnail_name)
    os.makedirs(os.path.dirname(thumb_out_path), exist_ok=True)
    shutil.move(thumbnail_path, thumb_out_path)

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
                thumbnail=Thumbnail(os.path.relpath(thumb_out_path, root)),
                date_saved=date_saved,
            )
        ],
    )

    documents = read_documents(root)
    documents.append(new_document)

    write_documents(root=root, documents=documents)

    return new_document


def pairwise_merge_documents(root, *, doc1, doc2, new_title, new_tags):
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


# def merge_documents(root, *, documents, new_title, new_tags)