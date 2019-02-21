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

    try:
        shutil.rmtree(root)
    except Exception:
        pass


@pytest.fixture
def pdf_file():
    return open("tests/snakes.pdf", "rb")


@pytest.fixture
def pdf_path(store):
    p = os.path.join(store.files_dir, "s/snakes.pdf")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    shutil.copyfile("tests/snakes.pdf", p)
    return "s/snakes.pdf"
