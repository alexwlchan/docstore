import datetime
import json
import uuid

import attr

from docstore.models import Document, DocumentEncoder


def test_document_defaults():
    d1 = Document()
    assert isinstance(d1.id, uuid.UUID)
    assert (datetime.datetime.now() - d1.date_created).seconds < 2
    assert d1.tags == []
    assert d1.files == []

    d2 = Document()
    assert d1.id != d2.id


def test_can_serialise_to_json():
    d = Document()
    json_string = json.dumps(attr.asdict(d), cls=DocumentEncoder)
    assert Document(**json.loads(json_string)) == d
