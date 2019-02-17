# -*- encoding: utf-8

import json
import os
import uuid

import attr


@attr.s(init=False)
class TaggedDocumentStore:
    root = attr.ib()
    documents = attr.ib()

    def __init__(self, root):
        self.root = root

        try:
            self.documents = json.load(open(self.db_path))
        except FileNotFoundError:
            self.documents = []

    @property
    def db_path(self):
        return os.path.join(self.root, "documents.json")

    @property
    def files_dir(self):
        return os.path.join(self.root, "files")

    @property
    def thumbs_dir(self):
        return os.path.join(self.root, "thumbnails")

    def index_document(self, doc):
        self.documents.append(doc)

        # Write to the database atomically.
        tmp_path = ".".join([self.db_path, str(uuid.uuid4()), "tmp"])
        with open(tmp_path, "w") as outfile:
            outfile.write(json.dumps(self.documents, indent=2, sort_keys=True))

        os.rename(tmp_path, self.db_path)

