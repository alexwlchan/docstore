# -*- encoding: utf-8

import hashlib
import mimetypes
import os
import shutil

import magic

from exceptions import UserError
from tagged_store import TaggedDocument
from thumbnails import create_jpeg_thumbnail


def create_thumbnail(store, doc):
    try:
        os.unlink(os.path.join(store.thumbnails_dir, doc["thumbnail_identifier"]))
    except KeyError:
        pass

    file_identifier = doc["file_identifier"]
    absolute_file_identifier = os.path.join(store.files_dir, file_identifier)
    thumb_path = os.path.join(doc.id[0], doc.id + ".jpg")

    absolute_thumb_path = os.path.join(store.thumbnails_dir, thumb_path)
    os.makedirs(os.path.dirname(absolute_thumb_path), exist_ok=True)

    thumbnail = create_jpeg_thumbnail(absolute_file_identifier)

    shutil.move(thumbnail, absolute_thumb_path)
    assert os.path.exists(absolute_thumb_path)

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
