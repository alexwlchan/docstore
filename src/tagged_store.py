# -*- encoding: utf-8

from collections.abc import MutableMapping
import datetime as dt
import json
import pathlib
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
                del data["id"]
                self.id = doc_id
        elif "id" in data:
            self.id = data["id"]
        elif doc_id is not None:
            self.id = doc_id
        else:
            self.id = str(uuid.uuid4())

        assert "date_created" not in data
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
        if isinstance(obj, TaggedDocument):
            return obj.data


def to_json(d, *args, **kwargs):
    kwargs["cls"] = TaggedDocumentEncoder
    return json.dumps(d, *args, **kwargs)


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
        json_string = to_json(new_documents, indent=2, sort_keys=True)

        # Write to the database atomically.
        tmp_path = self.db_path.parent / (
            self.db_path.name + str(uuid.uuid4()) + ".tmp")
        tmp_path.write_text(json_string)
        tmp_path.rename(self.db_path)

        # Don't write to the in-memory database until it's been saved to disk.
        self.documents = new_documents

    def index_document(self, doc_id, doc):
        assert not isinstance(doc, TaggedDocument)

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
