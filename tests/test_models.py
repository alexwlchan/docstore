import datetime
import uuid

import pytest

from docstore.models import Dimensions, Document, File, Thumbnail, from_json, to_json


def is_recent(ds):
    return (datetime.datetime.now() - ds).seconds < 2


def test_document_defaults():
    d1 = Document(title="My test document")
    assert uuid.UUID(d1.id)
    assert is_recent(d1.date_saved)
    assert d1.tags == []
    assert d1.files == []

    d2 = Document(title="A different document")
    assert d1.id != d2.id


def test_file_defaults():
    f = File(
        filename="cats.jpg",
        path="files/c/cats.jpg",
        size=100,
        checksum="sha256:123",
        thumbnail=Thumbnail(
            path="thumbnails/c/cats.jpg", dimensions=Dimensions(400, 300)
        ),
    )
    uuid.UUID(f.id)
    assert is_recent(f.date_saved)


def test_can_serialise_document_to_json():
    f = File(
        filename="cats.jpg",
        path="files/c/cats.jpg",
        size=100,
        checksum="sha256:123",
        thumbnail=Thumbnail(
            path="thumbnails/c/cats.jpg", dimensions=Dimensions(400, 300)
        ),
    )

    documents = [Document(title="Another test document", files=[f])]
    assert from_json(to_json(documents)) == documents


@pytest.mark.parametrize("documents", [[1, 2, 3], {"a", "b", "c"}])
def test_to_json_with_bad_list_is_typeerror(documents):
    with pytest.raises(TypeError, match=r"Expected type List\[Document\]!"):
        to_json(documents)
