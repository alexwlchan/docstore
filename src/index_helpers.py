# -*- encoding: utf-8

import hashlib
import mimetypes
import os
import pathlib
import shutil

import magic

from exceptions import UserError
from tagged_store import TaggedDocument
from thumbnails import create_thumbnail


def store_thumbnail(store, doc):
    try:
        (store.thumbnails_dir / doc["thumbnail_identifier"]).unlink()
    except KeyError:
        pass

    absolute_file_identifier = store.files_dir / doc["file_identifier"]

    thumb_dir = store.thumbnails_dir / doc.id[0]
    thumb_dir.mkdir(exist_ok=True)

    thumbnail = create_thumbnail(absolute_file_identifier)
    thumb_path = pathlib.Path(doc.id[0]) / (doc.id + thumbnail.suffix)

    absolute_thumb_path = store.thumbnails_dir / thumb_path

    shutil.move(thumbnail, absolute_thumb_path)
    assert absolute_thumb_path.exists()

    doc["thumbnail_identifier"] = thumb_path
    store.index_document(doc)


def index_document(store, user_data):
    doc = TaggedDocument(user_data)

    file_data = user_data.pop("file")

    try:
        # Try to guess an extension based on the filename provided by the user.
        _, extension = os.path.splitext(doc["filename"])
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

    file_identifier = os.path.join(doc.id[0], doc.id + extension)
    complete_file_identifier = os.path.join(store.files_dir, file_identifier)
    os.makedirs(os.path.dirname(complete_file_identifier), exist_ok=True)
    open(complete_file_identifier, "wb").write(file_data)
    doc["file_identifier"] = file_identifier

    # Add a SHA256 hash of the PDF.  This allows integrity checking later
    # and makes it easy to detect duplicates.
    # Note: this slurps the entire PDF in at once.  Fine for small files;
    # might be worth revisiting if I ever get something unusually large.
    h = hashlib.sha256()
    h.update(open(complete_file_identifier, "rb").read())
    try:
        if doc["sha256_checksum"] != h.hexdigest():
            raise UserError(
                "Incorrect SHA256 hash on upload!  Got %s, calculated %s." %
                (doc['sha256_checksum'], h.hexdigest())
            )
    except KeyError:
        doc["sha256_checksum"] = h.hexdigest()

    store.index_document(doc)
    return doc
