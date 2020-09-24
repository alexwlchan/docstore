import datetime
import json
import pathlib
from typing import List
import uuid

import attr
import cattr


def _convert_to_uuid(u):
    if isinstance(u, uuid.UUID):
        return u
    else:
        return uuid.UUID(u)


def _convert_to_datetime(d):
    if isinstance(d, datetime.datetime):
        return d
    else:
        return datetime.datetime.fromisoformat(d)


def _convert_to_thumbnail(t):
    if isinstance(t, Thumbnail):
        return t
    else:
        return Thumbnail(**t)


def _convert_to_file(f_list):
    return [f if isinstance(f, File) else File(**f) for f in f_list]


@attr.s
class Thumbnail:
    path = attr.ib(converter=pathlib.Path)


@attr.s
class File:
    filename = attr.ib(converter=pathlib.Path)
    path = attr.ib(type=str)
    size = attr.ib(type=int)
    checksum = attr.ib(type=str)
    thumbnail = attr.ib(type=Thumbnail, converter=_convert_to_thumbnail)
    source_url = attr.ib(type=str, default=None)
    date_saved = attr.ib(
        factory=datetime.datetime.now, converter=_convert_to_datetime
    )
    id = attr.ib(factory=uuid.uuid4, converter=_convert_to_uuid)


@attr.s
class Document:
    title = attr.ib(type=str)
    id = attr.ib(factory=uuid.uuid4, converter=_convert_to_uuid)
    date_saved = attr.ib(
        factory=datetime.datetime.now, converter=_convert_to_datetime
    )
    tags = attr.ib(factory=list)
    files = attr.ib(factory=list, converter=_convert_to_file)


class DocstoreEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, pathlib.Path):
            return str(obj)
        else:  # pragma: no cover
            return super().default(obj)


def to_json(documents):
    if not isinstance(documents, list) or not all(
        isinstance(d, Document) for d in documents
    ):
        raise TypeError("Expected type List[Document]!")

    # Use the same order that's used to serve the documents; Python's sort()
    # function goes faster if the documents are already in the right order.
    documents = sorted(documents, key=lambda d: d.date_saved, reverse=True)

    return json.dumps(
        cattr.unstructure(documents), indent=2, sort_keys=True, cls=DocstoreEncoder
    )


def from_json(json_string):
    return cattr.structure(json.loads(json_string), List[Document])
