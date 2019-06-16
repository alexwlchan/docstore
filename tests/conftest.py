# -*- encoding: utf-8

import pathlib
import shutil
import sys

import pytest

sys.path.append(str(pathlib.Path(__file__).parent.parent / "src"))

import api as service  # noqa
from file_manager import FileManager
from tagged_store import TaggedDocumentStore  # noqa


@pytest.fixture
def store_root(tmpdir):
    return pathlib.Path(tmpdir)


@pytest.fixture
def store(store_root):
    return TaggedDocumentStore(root=store_root)


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


@pytest.fixture
def tagged_store(store):
    return store.underlying


@pytest.fixture
def file_manager(tmpdir):
    return FileManager(root=pathlib.Path(tmpdir))
