import time

from docstore.files import read_documents, sha256, write_documents
from docstore.models import Document, to_json


def test_sha256():
    assert sha256("tests/files/cluster.png") == "sha256:683cbee0c2dda22b42fd92bda0f31e4b6b49cd8650a7924d72a14a30f11bfbe5"


def test_read_blank_documents_is_empty(tmpdir):
    assert read_documents(tmpdir) == []


def test_can_write_and_read_documents(tmpdir):
    documents = [Document(title="My first document")]

    write_documents(root=tmpdir, documents=documents)

    # Repeat a couple of times so we hit the caching paths.
    for _ in range(3):
        assert read_documents(tmpdir) == documents
