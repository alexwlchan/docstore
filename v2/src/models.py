import datetime
import json
import uuid

import attr


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


@attr.s
class Document:
    id = attr.ib(factory=uuid.uuid4, converter=_convert_to_uuid)
    date_created = attr.ib(factory=datetime.datetime.now, converter=_convert_to_datetime)
    tags = attr.ib(factory=list)
    files = attr.ib(factory=list)


def test_document_defaults():
    d1 = Document()
    assert isinstance(d1.id, uuid.UUID)
    assert (datetime.datetime.now() - d1.date_created).seconds < 2
    assert d1.tags == []
    assert d1.files == []

    d2 = Document()
    assert d1.id != d2.id


class DocumentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:  # pragma: no cover
            return obj


def test_can_serialise_to_json():
    d = Document()
    json_string = json.dumps(attr.asdict(d), cls=DocumentEncoder)
    assert Document(**json.loads(json_string)) == d
