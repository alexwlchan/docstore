#!/usr/bin/env python
"""
DB schema migration: v2.1.0 ~> v2.2.0

*   Record the tint color on Thumbnail instances.

"""

import datetime
import filecmp
import json
import os
import shutil
import sys

import tqdm

from docstore.git import current_commit
from docstore.tint_colors import choose_tint_color

OLD_DB_SCHEMA = "v2.1.0"
NEW_DB_SCHEMA = "v2.2.0"


if __name__ == "__main__":
    try:
        root = sys.argv[1]
    except IndexError:
        root = "."

    documents_path = os.path.join(root, "documents.json")
    backup_path = os.path.join(root, f"documents.{OLD_DB_SCHEMA}.json.bak")

    documents = json.load(open(documents_path))
    assert documents["docstore"]["db_schema"] == OLD_DB_SCHEMA

    # Backfill the thumbnail dimensions
    for doc in tqdm.tqdm(documents["documents"]):
        for f in doc["files"]:
            tint_color = choose_tint_color(
                thumbnail_path=os.path.join(root, f["thumbnail"]["path"]),
                file_path=os.path.join(root, f["path"]),
            )

            hex_tint_color = "#%02x%02x%02x" % tuple(
                int(component * 255) for component in tint_color
            )

            f["thumbnail"]["tint_color"] = hex_tint_color

    new_output = {
        "docstore": {
            "db_schema": NEW_DB_SCHEMA,
            "commit": current_commit(),
            "last_modified": datetime.datetime.now().isoformat(),
        },
        "documents": documents["documents"],
    }

    if os.path.exists(backup_path) and not filecmp.cmp(
        backup_path, documents_path, shallow=False
    ):
        raise RuntimeError("Have you already started a migration of this version?")

    shutil.copyfile(documents_path, backup_path)

    # Write the new database
    with open(documents_path, "w") as outfile:
        outfile.write(json.dumps(new_output, indent=2, sort_keys=True))
