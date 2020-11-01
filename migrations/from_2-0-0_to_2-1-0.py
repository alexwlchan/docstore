#!/usr/bin/env python
"""
DB schema migration: v2.0.0 ~> v2.1.0

*   Convert the document tree from a list of flat documents to a dict with some
    top-level metadata.
*   Record the dimension on Thumbnail instances.

"""

import datetime
import json
import os
import shutil
import sys

import cattr
import tqdm

from docstore.git import current_commit
from docstore.thumbnails import get_dimensions
from exceptions import IncorrectSchemaError

OLD_DB_SCHEMA = "v2.0.0"
NEW_DB_SCHEMA = "v2.1.0"


if __name__ == "__main__":
    try:
        root = sys.argv[1]
    except IndexError:
        root = "."

    documents_path = os.path.join(root, "documents.json")
    backup_path = os.path.join(root, f"documents.{OLD_DB_SCHEMA}.json.bak")

    # assert not os.path.exists(backup_path)
    shutil.copyfile(documents_path, backup_path)

    documents = json.load(open(documents_path))

    if not isinstance(documents, list):
        raise IncorrectSchemaError(
            f"The docstore instance at {root} doesn't look like {OLD_DB_SCHEMA}"
        )

    # Create the new top-level structure
    new_structure = {
        "docstore": {
            "db_schema": NEW_DB_SCHEMA,
            "commit": current_commit(),
            "last_modified": datetime.datetime.now().isoformat(),
        },
        "documents": documents,
    }

    # Backfill the thumbnail dimensions
    for doc in tqdm.tqdm(documents):
        for f in doc["files"]:
            dimensions = get_dimensions(os.path.join(root, f["thumbnail"]["path"]))
            f["thumbnail"]["dimensions"] = cattr.unstructure(dimensions)

    # Write the new database
    with open(documents_path, "w") as outfile:
        outfile.write(json.dumps(new_structure, indent=2, sort_keys=True))
