# -*- encoding: utf-8

import json
import pathlib
import uuid

import attr


class PosixPathEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pathlib.Path):
            return str(obj)


@attr.s(init=False)
class TaggedDocumentStore:
    root = attr.ib()
    documents = attr.ib()

    def __init__(self, root):
        self.root = pathlib.Path(root)

        try:
            self.documents = json.load(open(self.db_path))
        except FileNotFoundError:
            self.documents = {}

        self.files_dir.mkdir(exist_ok=True)
        self.thumbnails_dir.mkdir(exist_ok=True)

    @property
    def db_path(self):
        return self.root / "documents.json"

    @property
    def files_dir(self):
        return self.root / "files"

    @property
    def thumbnails_dir(self):
        return self.root / "thumbnails"

    def save(self, new_documents):
        json_string = json.dumps(
            new_documents,
            indent=2,
            sort_keys=True,
            cls=PosixPathEncoder
        )

        # Write to the database atomically.
        tmp_path = self.db_path.parent / (
            self.db_path.name + str(uuid.uuid4()) + ".tmp")
        tmp_path.write_text(json_string)
        tmp_path.rename(self.db_path)

        # Don't write to the in-memory database until it's been saved to disk.
        self.documents = new_documents

    def index_document(self, doc_id, doc):
        new_documents = self.documents.copy()
        new_documents[doc_id] = doc

        self.save(new_documents)

    def search_documents(self, query):
        return [
            doc
            for doc in self.documents.values()
            if matches_tag_query(doc, query)
        ]


def matches_tag_query(doc, query):
    tags = set(doc.get("tags", []))
    return all(q in tags for q in query)
