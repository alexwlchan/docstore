#!/usr/bin/env python
# -*- encoding: utf-8

import hashlib
import logging
import json
import os
import tarfile
import time

import daiquiri


daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


def sha256(path):
    h = hashlib.sha256()
    h.update(open(path, "rb").read())
    return h.hexdigest()


def list_docstore_instances(docstore_root):
    for root, _, filenames in os.walk(docstore_root):
        if "documents.json" in filenames:
            yield os.path.basename(root), root


for name, root in list_docstore_instances("/mnt/docstore"):
    logger.info("Checking docstore instance at %s", root)

    store_data = json.load(open(os.path.join(root, "documents.json")))
    logger.info("Loaded %d documents for %s", len(store_data), name)

    recognised_files = set()
    warnings = 0
    errors = 0

    for doc_id, doc_data in store_data.items():
        logger.debug("Checking document ID %s", doc_id)
        file_identifier = doc_data["file_identifier"]
        try:
            actual_sha256 = sha256(os.path.join(root, "files", file_identifier))
        except FileNotFoundError:
            logger.error("Unable to find original file for %s", doc_id)
            errors += 1
            continue

        recognised_files.add(file_identifier)

        if actual_sha256 != doc_data["sha256_checksum"]:
            logger.warn(
                "SHA256 checksums for %s do not match: %s != %s",
                doc_id, actual_sha256, doc_data["sha256_checksum"]
            )
            warnings += 1

    if errors == 0 and warnings == 0:
        logger.info("Checked %s with no errors or warnings", name)
    elif errors == 0 and warnings > 0:
        logger.warning("Checked %s with %d warning%s", name, warnings, "s" if warnings > 1 else "")
    elif errors > 0 and warnings == 0:
        logger.error("Checked %s with %d error%s", name, errors, "s" if errors > 1 else "")
    else:
        logger.error("Checked %s with %d error%s and %d warning%s", name, errors, "s" if errors > 1 else "", warnings, "s" if warnings > 1 else "")

    all_files = os.path.join(root, "files")
    for f_root, _, f_filenames in os.walk(all_files):
        for filename in f_filenames:
            path = os.path.join(f_root, filename)
            file_identifier = os.path.relpath(path, start=all_files)
            if file_identifier not in recognised_files:
                logger.warning("Detected unrecognised file: %s", file_identifier)


with tarfile.open(name="snapshot.%s.tar.gz" % int(time.time()), mode="w") as tf:
    for name, root in list_docstore_instances("/mnt/docstore"):
        tf.add(root, arcname=os.path.join("docstore", name))

    logger.info("Created archive as %s", os.path.basename(tf.name))

