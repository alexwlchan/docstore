#!/usr/bin/env python
# -*- encoding: utf-8
"""
Move any files in the `/files` directory that aren't referred to in the database
out of the main folder.
"""

import json
import os
import pathlib
import sys


if __name__ == "__main__":
    try:
        root = sys.argv[1]
    except IndexError:
        sys.exit(f"Usage: {__file__} <ROOT>")

    root = pathlib.Path(root)
    documents = root / "documents.json"

    with documents.open() as infile:
        documents_data = json.load(infile)

    referenced_files = set(d["file_identifier"] for d in documents_data.values())

    for file_root, _, filenames in os.walk(root / "files"):
        for f in filenames:
            path = pathlib.Path(file_root) / f
            relpath = path.relative_to(root / "files")
            if str(relpath) not in referenced_files:
                (root / "unreferenced").mkdir(exist_ok=True)
                target = root / "unreferenced" / f
                if not target.exists():
                    print(relpath)
                    path.rename(root / "unreferenced" / f)
