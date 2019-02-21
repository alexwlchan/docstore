# -*- encoding: utf-8

import shutil
import tempfile

import pytest

from tagged_store import TaggedDocumentStore


@pytest.fixture
def store():
    root = tempfile.mkdtemp()
    yield TaggedDocumentStore(root=root)
    shutil.rmtree(root)


@pytest.fixture
def pdf_file():
    return open("tests/snakes.pdf", "rb")
