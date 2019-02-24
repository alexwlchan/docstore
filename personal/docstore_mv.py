#!/usr/bin/env python
# -*- encoding: utf-8

import os
import shutil
import subprocess
import sys

import click

sys.path.append("../src")
from tagged_store import TaggedDocumentStore  # noqa


DOCSTORE_ROOT = os.path.join(os.environ["HOME"], "Documents", "docstore")

KNOWN_STORES = [
    d
    for d in os.listdir(DOCSTORE_ROOT)
    if os.path.isdir(os.path.join(DOCSTORE_ROOT, d))
]


def get_store_name(resp):
    matching = [d for d in KNOWN_STORES if d.startswith(resp)]
    if len(matching) > 1:
        sys.exit("Ambiguous store for %r: %s" % (resp, ", ".join(matching)))
    elif not matching:
        sys.exit("No store found for %r" % resp)

    if matching[0] != resp:
        print("Detected store as %r" % matching[0])

    return matching[0]


@click.command()
@click.option("--src", prompt="Which store are you moving from?", required=True)
@click.option("--dst", prompt="Which store are you moving to?", required=True)
@click.option("--skip-restart", is_flag=True)
def main(src, dst, skip_restart):
    src_name = get_store_name(src)
    src_store = TaggedDocumentStore(os.path.join(DOCSTORE_ROOT, src_name))

    dst_name = get_store_name(dst)
    assert src_name != dst_name
    dst_store = TaggedDocumentStore(os.path.join(DOCSTORE_ROOT, dst_name))

    src_id = click.prompt("Which document do you want to move?")
    matching_ids = [
        doc
        for doc in src_store.documents.values()
        if doc["id"].startswith(src_id)
    ]
    if len(matching_ids) > 1:
        sys.exit("Ambiguous ID!  Specify a longer prefix.")
    elif not matching_ids:
        sys.exit("No IDs found!")

    doc_to_move = matching_ids[0]

    src_file = os.path.join(src_store.files_dir, doc_to_move["file_identifier"])
    dst_file = os.path.join(dst_store.files_dir, doc_to_move["file_identifier"])
    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
    shutil.copyfile(src_file, dst_file)

    src_thumb = os.path.join(src_store.thumbnails_dir, doc_to_move["thumbnail_identifier"])
    dst_thumb = os.path.join(dst_store.thumbnails_dir, doc_to_move["thumbnail_identifier"])
    os.makedirs(os.path.dirname(dst_thumb), exist_ok=True)
    shutil.copyfile(src_thumb, dst_thumb)

    dst_store.index_document(doc_to_move)

    del src_store.documents[doc_to_move["id"]]
    src_store.save(new_documents=src_store.documents)

    os.unlink(os.path.join(src_store.files_dir, doc_to_move["file_identifier"]))
    os.unlink(os.path.join(src_store.thumbnails_dir, doc_to_move["thumbnail_identifier"]))

    if not skip_restart:
        subprocess.check_call(["docker-compose", "restart"])


if __name__ == "__main__":
    main()
