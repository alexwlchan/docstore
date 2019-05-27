# -*- encoding: utf-8

import json
import pathlib


class TaggedDocumentEncoder(json.JSONEncoder):
    def default(self, obj):
        from tagged_store import TaggedDocument
        if isinstance(obj, TaggedDocument):
            return obj.data
        elif isinstance(obj, pathlib.Path):
            return str(obj)


def to_json(d, *args, **kwargs):
    kwargs["cls"] = TaggedDocumentEncoder
    return json.dumps(d, *args, **kwargs)


def from_json(s):
    if isinstance(s, str):
        return json.loads(s)
    else:
        return json.load(s)
