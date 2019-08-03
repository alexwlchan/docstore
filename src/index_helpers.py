# -*- encoding: utf-8

import datetime as dt
import hashlib

from exceptions import UserError


def index_new_document(tagged_object_store, file_manager, doc_id, doc):
    assert "date_created" not in doc
    doc["date_created"] = dt.datetime.now().isoformat()

    file_data = doc.pop("file")

    file_identifier = file_manager.write_bytes(
        file_id=doc_id,
        buffer=file_data,
        original_filename=doc.get("filename")
    )

    doc["file_identifier"] = file_identifier

    # Add a SHA256 hash of the PDF.  This allows integrity checking later
    # and makes it easy to detect duplicates.
    h = hashlib.sha256()
    h.update(file_data)
    checksum_value = h.hexdigest()

    doc["checksum"] = f"sha256:{checksum_value}"

    tagged_object_store.init(obj_id=doc_id, obj_data=doc)
    return doc
