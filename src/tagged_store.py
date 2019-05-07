# -*- encoding: utf-8

from collections.abc import MutableMapping
import datetime as dt
import json
import os
import uuid

import attr


@attr.s(init=False, cmp=False)
class TaggedDocument(MutableMapping):
    id = attr.ib()
    data = attr.ib()
    tags = attr.ib()

    def __init__(self, data, doc_id=None):
        if ("id" in data) and (doc_id is not None):
            if data["id"] != doc_id:
                raise ValueError(f"IDs must match: {data['id']!r} != {doc_id!r}")
            else:
                self.id = data["id"]
        elif "id" in data:
            self.id = data["id"]
        elif doc_id is not None:
            self.id = doc_id
        else:
            self.id = str(uuid.uuid4())

        if "date_created" not in data:
            data["date_created"] = dt.datetime.now().isoformat()

        self.data = data

    @property
    def tags(self):
        return set(self.data.get("tags", []))

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

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
            doc_id: TaggedDocument(doc_id=doc_id, data=data)
            for doc_id, data in existing.items()
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

    def save(self, new_documents):
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

    def index_document(self, doc, doc_id=None):
        if isinstance(doc, dict):
            doc = TaggedDocument(doc, doc_id=doc_id)

        if not isinstance(doc, TaggedDocument):
            raise TypeError("doc=%r is %s, expected TaggedDocument" % (doc, type(doc)))

        new_documents = self.documents.copy()
        new_documents[doc.id] = doc

        self.save(new_documents)

        return doc

    def search_documents(self, query):
        return [
            doc
            for doc in self.documents.values()
            if doc.matches_tag_query(query)
        ]
