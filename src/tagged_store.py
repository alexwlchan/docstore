# -*- encoding: utf-8

import json
import os
import uuid

import attr


@attr.s(init=False, cmp=False)
class TaggedDocument:
    data = attr.ib()
    tags = attr.ib()

    def __init__(self, data):
        self.data = data
        self.tags = set(data.get("tags", []))

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

        self.documents = {
            doc_id: TaggedDocument(doc)
            for doc_id, doc in existing.items()
        }

    @property
    def db_path(self):
        return os.path.join(self.root, "documents.json")

    @property
    def files_dir(self):
        return os.path.join(self.root, "files")

    @property
    def thumbs_dir(self):
        return os.path.join(self.root, "thumbnails")

    def index_document(self, doc, doc_id=None):
        if isinstance(doc, dict):
            doc = TaggedDocument(doc)

        if not isinstance(doc, TaggedDocument):
            raise TypeError("doc=%r is %s, expected TaggedDocument" % (doc, type(doc)))

        if doc_id is None:
            try:
                doc_id = doc.data["_id"]
            except KeyError:
                doc_id = str(uuid.uuid4())
                doc.data["_id"] = doc_id

        new_documents = self.documents.copy()
        new_documents[doc_id] = doc

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
