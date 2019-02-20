# -*- encoding: utf-8

import datetime as dt
import json
import os
import uuid

import attr


@attr.s(init=False, cmp=False)
class TaggedDocument:
    data = attr.ib()
    tags = attr.ib()

    def __init__(self, data):
        if "id" not in data:
            data["id"] = str(uuid.uuid4())

        if "date_created" not in data:
            data["date_created"] = dt.datetime.now().isoformat()

        self.data = data
        self.tags = set(data.get("tags", []))

    @property
    def id(self):
        return self.data["id"]

    @property
    def date_created(self):
        return self.data["date_created"]

    def __eq__(self, other):
        if isinstance(other, TaggedDocument):
            return self.data == other.data
        elif isinstance(other, dict):
            return self.data == other
        else:
            return NotImplemented

    def __hash__(self):
        # Dicts are unhashable; the same is true for TaggedDocument
        raise TypeError("unhashable type: %r" % type(self).__name__)

    def matches_tag_query(self, query):
        return all(q in self.tags for q in query)


class TaggedDocumentEncoder(json.JSONEncoder):
    def default(self, obj):
        assert isinstance(obj, TaggedDocument)
        return obj.data


@attr.s(init=False)
class TaggedDocumentStore:
    root = attr.ib()
    documents = attr.ib()

    def __init__(self, root):
        self.root = root

        try:
            existing = json.load(open(self.db_path))
        except FileNotFoundError:
            existing = {}

        os.makedirs(self.files_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)

        self.documents = {
            docid: TaggedDocument(doc)
            for docid, doc in existing.items()
        }

    @property
    def db_path(self):
        return os.path.join(self.root, "documents.json")

    @property
    def files_dir(self):
        return os.path.join(self.root, "files")

    @property
    def thumbnails_dir(self):
        return os.path.join(self.root, "thumbnails")

    def index_document(self, doc):
        if isinstance(doc, dict):
            doc = TaggedDocument(doc)

        if not isinstance(doc, TaggedDocument):
            raise TypeError("doc=%r is %s, expected TaggedDocument" % (doc, type(doc)))

        new_documents = self.documents.copy()
        new_documents[doc.id] = doc

        json_string = json.dumps(
            new_documents,
            indent=2,
            sort_keys=True,
            cls=TaggedDocumentEncoder
        )

        # Write to the database atomically.
        tmp_path = ".".join([self.db_path, str(uuid.uuid4()), "tmp"])
        with open(tmp_path, "w") as outfile:
            outfile.write(json_string)

        os.rename(tmp_path, self.db_path)

        # We deliberately don't write to the in-memory database until it's been
        # persisted to disk.
        self.documents = new_documents

    def search_documents(self, query):
        return [
            doc
            for doc in self.documents.values()
            if doc.matches_tag_query(query)
        ]
