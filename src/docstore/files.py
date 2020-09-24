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
    if (
        _cached_documents["last_modified"] is not None and
        os.stat(db_path).st_mtime <= _cached_documents["last_modified"]
    ):
        return _cached_documents["contents"]

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

    out_path = os.path.join("files", slug[0], slug)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    while os.path.exists(out_path):
        out_path = os.path.join(
            "files", slug[0], slugify(name) + "_" + secrets.token_hex(2) + ext
        )

    shutil.move(path, out_path)

    thumbnail_path = create_thumbnail(out_path)
    thumbnail_name = os.path.basename(thumbnail_path)
    thumb_out_path = os.path.join("thumbnails", thumbnail_name[0], thumbnail_name)
    os.makedirs(os.path.dirname(thumb_out_path), exist_ok=True)
    shutil.move(thumbnail_path, thumb_out_path)

    documents = read_documents(root)
    documents.append(
        Document(
            title=title,
            date_saved=date_saved,
            tags=tags,
            files=[
                File(
                    filename=filename,
                    path=out_path,
                    size=os.stat(out_path).st_size,
                    checksum=sha256(out_path),
                    source_url=source_url,
                    thumbnail=Thumbnail(thumb_out_path),
                    date_saved=date_saved,
                )
            ],
        )
    )

    write_documents(root=root, documents=documents)
