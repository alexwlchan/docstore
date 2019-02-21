# -*- encoding: utf-8

import shutil
import tempfile

import os
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


@pytest.fixture
def pdf_path(store, pdf_file):
    p = os.path.join(store.files_dir, "s/snakes.pdf")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(pdf_file.read())
    return "s/snakes.pdf"
