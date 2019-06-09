# -*- encoding: utf-8

import pathlib

import attr

from storage import JsonTaggedObjectStore


@attr.s(init=False)
class TaggedDocumentStore:
    root = attr.ib()

    def __init__(self, root):
        self.root = pathlib.Path(root)
        self.underlying = JsonTaggedObjectStore(self.root / "documents.json")

        self.files_dir.mkdir(exist_ok=True)
        self.thumbnails_dir.mkdir(exist_ok=True)

    @property
    def files_dir(self):
        return self.root / "files"

    @property
    def thumbnails_dir(self):
        return self.root / "thumbnails"
