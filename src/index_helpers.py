# -*- encoding: utf-8

import hashlib
import os
import shutil
import subprocess
import tempfile

from preview_generator.manager import PreviewManager

from exceptions import UserError
from tagged_store import TaggedDocument


preview_manager = PreviewManager(tempfile.mkdtemp())


def create_thumbnail(store, doc):
    try:
        os.unlink(os.path.join(store.thumbnails_dir, doc["thumbnail_path"]))
    except KeyError:
        pass

    pdf_path = doc["pdf_path"]
    absolute_pdf_path = os.path.join(store.files_dir, pdf_path)
    thumb_path = os.path.join(doc.id[0], doc.id + ".jpg")

    absolute_thumb_path = os.path.join(store.thumbnails_dir, thumb_path)
    os.makedirs(os.path.dirname(absolute_thumb_path), exist_ok=True)

    thumbnail = preview_manager.get_jpeg_preview(
        absolute_pdf_path,
        height=400,
        width=400
    )

    shutil.move(thumbnail, absolute_thumb_path)
    assert os.path.exists(absolute_thumb_path)

    doc["thumbnail_path"] = thumb_path
    store.index_document(doc)


def index_pdf_document(store, user_data):
    doc = TaggedDocument(user_data)

    pdf_path = os.path.join(doc.id[0], doc.id + ".pdf")
    complete_pdf_path = os.path.join(store.files_dir, pdf_path)
    os.makedirs(os.path.dirname(complete_pdf_path), exist_ok=True)
    open(complete_pdf_path, "wb").write(user_data.pop("file"))
    doc["pdf_path"] = pdf_path

    # Add a SHA256 hash of the PDF.  This allows integrity checking later
    # and makes it easy to detect duplicates.
    # Note: this slurps the entire PDF in at once.  Fine for small files;
    # might be worth revisiting if I ever get something unusually large.
    h = hashlib.sha256()
    h.update(open(complete_pdf_path, "rb").read())
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
