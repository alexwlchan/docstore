#!/usr/bin/env python
# -*- encoding: utf-8
"""
Modify an existing database so that it uses human-friendly filenames instead
of UUIDs to name files in the underlying storage.

Usage:

    python use_human_friendly_filenames.py <ROOT>

Then restart your docstore instance.

"""

import filecmp
import json
import pathlib
import shutil
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent / "src"))

from file_manager import FileManager
from storage.object_store import PosixPathEncoder


if __name__ == "__main__":
    try:
        root = sys.argv[1]
    except IndexError:
        sys.exit(f"Usage: {__file__} <ROOT>")

    root = pathlib.Path(root)
    documents = root / "documents.json"

    shutil.copyfile(documents, root / "documents.json.bak")

    with documents.open() as infile:
        documents_data = json.load(infile)

    fm = FileManager(root / "files")

    to_delete = set()

    for doc_id, doc in documents_data.items():
        if "filename" not in doc:
            continue

        if not doc["file_identifier"].startswith(doc_id[0] + "/" + doc_id):
            continue

        new_identifier = fm.write_bytes(
            file_id=doc_id,
            buffer=(root / "files" / doc["file_identifier"]).read_bytes(),
            original_filename=doc["filename"]
        )

        assert filecmp.cmp(
            root / "files" / doc["file_identifier"],
            root / "files" / new_identifier
        )

        print(f"{doc['file_identifier']} ~> {new_identifier}")

        to_delete.add(doc["file_identifier"])
        doc["file_identifier"] = new_identifier

    json_string = json.dumps(
        documents_data,
        indent=2,
        sort_keys=True,
        cls=PosixPathEncoder
    )
    documents.write_text(json_string)
