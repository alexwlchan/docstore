import datetime
import json
import uuid

import attr

from docstore.models import Document, File, Thumbnail, from_json, to_json


def test_document_defaults():
    d1 = Document()
    assert isinstance(d1.id, uuid.UUID)
    assert (datetime.datetime.now() - d1.date_created).seconds < 2
    assert d1.tags == []
    assert d1.files == []

    d2 = Document()
    assert d1.id != d2.id


def test_file_defaults():
    f = File(
        filename="cats.jpg",
        path="files/c/cats.jpg",
        size=100,
        checksum="sha256:123",
        thumbnail=Thumbnail(path="thumbnails/c/cats.jpg"),
    )
    assert isinstance(f.id, uuid.UUID)


def test_can_serialise_document_to_json():
    f = File(
        filename="cats.jpg",
        path="files/c/cats.jpg",
        size=100,
        checksum="sha256:123",
        thumbnail=Thumbnail(path="thumbnails/c/cats.jpg"),
    )

    documents = [Document(files=[f])]
    assert from_json(to_json(documents)) == documents
