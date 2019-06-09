# -*- encoding: utf-8

import datetime as dt
import mimetypes
import pathlib
import shutil

import magic

from exceptions import UserError
from hash_helpers import sha256
from thumbnails import create_thumbnail


def store_thumbnail(store, doc_id, doc):
    try:
        (store.thumbnails_dir / doc["thumbnail_identifier"]).unlink()
    except KeyError:
        pass

    absolute_file_identifier = store.files_dir / doc["file_identifier"]

    thumb_dir = store.thumbnails_dir / doc_id[0]
    thumb_dir.mkdir(exist_ok=True)

    thumbnail = create_thumbnail(absolute_file_identifier)
    thumb_path = pathlib.Path(doc_id[0]) / (doc_id + thumbnail.suffix)

    absolute_thumb_path = store.thumbnails_dir / thumb_path

    shutil.move(thumbnail, absolute_thumb_path)
    assert absolute_thumb_path.exists()

    doc["thumbnail_identifier"] = thumb_path
    store.underlying.put(obj_id=doc_id, obj_data=doc)


def index_new_document(store, doc_id, doc):
    if doc_id in store.documents:
        raise ValueError(f"The store already has a document with id {doc_id}!")

    assert "date_created" not in doc
    doc["date_created"] = dt.datetime.now().isoformat()

    file_data = doc.pop("file")

    try:
        # Try to guess an extension based on the filename provided by the user.
        extension = pathlib.Path(doc["filename"]).suffix
    except KeyError:

        # If we didn't get a filename from the user, try to guess one based
        # on the data.  Note that mimetypes will suggest ".jpe" for JPEG images,
        # so replace it with the more common extension by hand.
        assert isinstance(file_data, bytes)
        guessed_mimetype = magic.from_buffer(file_data, mime=True)
        if guessed_mimetype == "image/jpeg":
            extension = ".jpg"
        else:
            extension = mimetypes.guess_extension(guessed_mimetype)

    if extension is None:
        extension = ""

    file_identifier = pathlib.Path(doc_id[0]) / (doc_id + extension)
    complete_file_identifier = store.files_dir / file_identifier
    complete_file_identifier.parent.mkdir(exist_ok=True)
    complete_file_identifier.write_bytes(file_data)
    doc["file_identifier"] = file_identifier

    # Add a SHA256 hash of the PDF.  This allows integrity checking later
    # and makes it easy to detect duplicates.
    actual_sha256 = sha256(complete_file_identifier.open("rb"))
    try:
        if doc["sha256_checksum"] != actual_sha256:
            raise UserError(
                "Incorrect SHA256 hash on upload!  Got %s, calculated %s." %
                (doc['sha256_checksum'], actual_sha256)
            )
    except KeyError:
        doc["sha256_checksum"] = actual_sha256

    store.underlying.put(obj_id=doc_id, obj_data=doc)
    return doc
