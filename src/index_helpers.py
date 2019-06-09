# -*- encoding: utf-8

import datetime as dt
import hashlib

from exceptions import UserError
from file_manager import FileManager


def index_new_document(store, doc_id, doc):
    assert "date_created" not in doc
    doc["date_created"] = dt.datetime.now().isoformat()

    file_data = doc.pop("file")

    manager = FileManager(store.files_dir)

    file_identifier = manager.write_bytes(
        file_id=doc_id,
        buffer=file_data,
        original_filename=doc.get("filename")
    )

    doc["file_identifier"] = file_identifier

    # Add a SHA256 hash of the PDF.  This allows integrity checking later
    # and makes it easy to detect duplicates.
    h = hashlib.sha256()
    h.update(file_data)
    actual_sha256 = h.hexdigest()

    try:
        if doc["sha256_checksum"] != actual_sha256:
            raise UserError(
                "Incorrect SHA256 hash on upload!  Got %s, calculated %s." %
                (doc['sha256_checksum'], actual_sha256)
            )
    except KeyError:
        doc["sha256_checksum"] = actual_sha256

    store.underlying.init(obj_id=doc_id, obj_data=doc)
    return doc
