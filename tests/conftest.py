# -*- encoding: utf-8

import pathlib
import shutil
import sys

import pytest

sys.path.append(str(pathlib.Path(__file__).parent.parent / "src"))

import api as service  # noqa
from file_manager import FileManager
from storage import MemoryTaggedObjectStore


@pytest.fixture
def store_root(tmpdir):
    return pathlib.Path(tmpdir)


@pytest.fixture
def pdf_path():
    return pathlib.Path("tests/files/snakes.pdf")


@pytest.fixture
def pdf_file(pdf_path):
    return pdf_path.open("rb")


@pytest.fixture
def file_identifier(store_root, pdf_path):
    p = store_root / "files" / "s/snakes.pdf"
    p.parent.mkdir(exist_ok=True, parents=True)
    shutil.copyfile(pdf_path, p)
    return "s/snakes.pdf"


@pytest.fixture()
def api(tagged_store, store_root):
    return service.create_api(tagged_store, root=store_root)


@pytest.fixture
def tagged_store():
    return MemoryTaggedObjectStore(initial_objects={})


@pytest.fixture
def file_manager(store_root):
    return FileManager(root=store_root)
