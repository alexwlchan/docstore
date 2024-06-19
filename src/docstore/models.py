import datetime
import json
import typing
import uuid

import attr
import cattr

from docstore.git import current_commit


DB_SCHEMA = "v2.2.0"


def _convert_to_datetime(d: datetime.datetime | str) -> datetime.datetime:
    if isinstance(d, datetime.datetime):
        return d
    else:
        return datetime.datetime.fromisoformat(d)


def _convert_to_thumbnail(t: typing.Any) -> "Thumbnail":
    if isinstance(t, Thumbnail):
        return t
    else:
        return Thumbnail(**t)


def _convert_to_dimensions(d: typing.Any) -> "Dimensions":
    if isinstance(d, Dimensions):
        return d
    else:
        return Dimensions(**d)


def _convert_to_file(f_list: list[typing.Any]) -> "list[File]":
    return [f if isinstance(f, File) else File(**f) for f in f_list]


@attr.s
class Dimensions:
    width: int = attr.ib()
    height: int = attr.ib()


@attr.s
class Thumbnail:
    path: str = attr.ib()
    dimensions: Dimensions = attr.ib(converter=_convert_to_dimensions)
    tint_color: str = attr.ib()


@attr.s
class File:
    filename: str = attr.ib(converter=str)
    path: str = attr.ib()
    size: int = attr.ib()
    checksum: str = attr.ib()
    thumbnail: Thumbnail = attr.ib(converter=_convert_to_thumbnail)
    source_url: str | None = attr.ib(default=None)
    date_saved: datetime.datetime = attr.ib(
        factory=datetime.datetime.now, converter=_convert_to_datetime
    )
    id: str = attr.ib(default=attr.Factory(lambda: str(uuid.uuid4())))


@attr.s
class Document:
    title: str = attr.ib()
    id: str = attr.ib(default=attr.Factory(lambda: str(uuid.uuid4())))
    date_saved: datetime.datetime = attr.ib(
        factory=datetime.datetime.now, converter=_convert_to_datetime
    )
    tags: list[str] = attr.ib(factory=list)
    files: list[File] = attr.ib(factory=list, converter=_convert_to_file)


class DocstoreEncoder(json.JSONEncoder):
    def default(self, obj: typing.Any) -> typing.Any:
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:  # pragma: no cover
            return super().default(obj)


def to_json(documents: list[Document]) -> str:
    """
    Returns a JSON string containing all the documents.
    """
    if not isinstance(documents, list) or not all(
        isinstance(d, Document) for d in documents
    ):
        raise TypeError("Expected type List[Document]!")

    # Use the same order that's used to serve the documents; Python's sort()
    # function goes faster if the documents are already in the right order.
    documents = sorted(documents, key=lambda d: d.date_saved, reverse=True)

    return json.dumps(
        {
            "docstore": {
                "db_schema": DB_SCHEMA,
                "commit": current_commit(),
                "last_modified": datetime.datetime.now().isoformat(),
            },
            "documents": cattr.unstructure(documents),
        },
        indent=2,
        sort_keys=True,
        cls=DocstoreEncoder,
    )


def from_json(json_string: str) -> list[Document]:
    """
    Parses a JSON string containing all the documents.
    """
    parsed_structure = json.loads(json_string)
    assert parsed_structure["docstore"]["db_schema"] == DB_SCHEMA
    return cattr.structure(parsed_structure["documents"], list[Document])
