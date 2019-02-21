# -*- encoding: utf-8

import hashlib
import os
import shutil
import tempfile

from preview_generator.manager import PreviewManager

from exceptions import UserError
from tagged_store import TaggedDocument


preview_manager = PreviewManager(tempfile.mkdtemp())


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

    thumbnail = preview_manager.get_jpeg_preview(
        absolute_file_identifier,
        height=400,
        width=400
    )

    shutil.move(thumbnail, absolute_thumb_path)
    assert os.path.exists(absolute_thumb_path)

    doc["thumbnail_identifier"] = thumb_path
    store.index_document(doc)


def index_document(store, user_data):
    doc = TaggedDocument(user_data)

    file_identifier = os.path.join(doc.id[0], doc.id + ".pdf")
    complete_file_identifier = os.path.join(store.files_dir, file_identifier)
    os.makedirs(os.path.dirname(complete_file_identifier), exist_ok=True)
    open(complete_file_identifier, "wb").write(user_data.pop("file"))
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
