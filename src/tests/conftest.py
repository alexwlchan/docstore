# -*- encoding: utf-8

import pathlib
import shutil

import pytest

import api as service
from tagged_store import TaggedDocumentStore


@pytest.fixture
def store(tmpdir):
    return TaggedDocumentStore(root=tmpdir)


@pytest.fixture
def pdf_path():
    return pathlib.Path("tests/files/snakes.pdf")


@pytest.fixture
def pdf_file(pdf_path):
    return pdf_path.open("rb")


@pytest.fixture
def file_identifier(store, pdf_path):
    p = store.files_dir / "s/snakes.pdf"
    p.parent.mkdir(exist_ok=True)
    shutil.copyfile(pdf_path, p)
    return "s/snakes.pdf"


@pytest.fixture()
def api(store):
    return service.create_api(store)
