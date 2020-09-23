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


class DocumentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:  # pragma: no cover
            return obj
