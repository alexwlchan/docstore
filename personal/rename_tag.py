#!/usr/bin/env python
# -*- encoding: utf-8

import os
import subprocess
import sys

import click

sys.path.append("../src")
from tagged_store import TaggedDocumentStore  # noqa

from docstore_mv import get_store_name, DOCSTORE_ROOT


@click.command()
@click.option("--store", prompt="Which store are you working in?", required=True)
@click.option("--old_tag", prompt="What's the old tag?", required=True)
@click.option("--new_tag", prompt="What's the new tag?", required=True)
def main(store, old_tag, new_tag):
    store_name = get_store_name(store)
    store = TaggedDocumentStore(os.path.join(DOCSTORE_ROOT, store_name))

    for doc in store.documents.values():
        try:
            doc["tags"][doc["tags"].index(old_tag)] = new_tag
        except ValueError:
            pass

    store.save(new_documents=store.documents)

    subprocess.check_call(["docker-compose", "restart", store_name])


if __name__ == "__main__":
    main()
