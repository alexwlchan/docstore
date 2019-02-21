# -*- encoding: utf-8

import os
import shutil

import pytest

from tagged_store import TaggedDocumentStore


@pytest.fixture
def store(tmpdir):
    return TaggedDocumentStore(root=str(tmpdir))


@pytest.fixture
def pdf_file():
    return open("tests/snakes.pdf", "rb")


@pytest.fixture
def file_identifier(store):
    p = os.path.join(store.files_dir, "s/snakes.pdf")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    shutil.copyfile("tests/snakes.pdf", p)
    return "s/snakes.pdf"
