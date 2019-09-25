# -*- encoding: utf-8

import datetime as dt
import pathlib
import random
import shutil
import sys

import pytest

import helpers

sys.path.append(str(pathlib.Path(__file__).parent.parent / "src"))

import api, config  # noqa
from file_manager import FileManager  # noqa
from storage import MemoryTaggedObjectStore  # noqa


@pytest.fixture
def store_root(tmpdir):
    return pathlib.Path(tmpdir)


@pytest.fixture
def pdf_path():
    return pathlib.Path("tests/files/snakes.pdf")


@pytest.fixture
def pdf_file(pdf_path):
    with pdf_path.open("rb") as f:
        yield f


@pytest.fixture
def png_path():
    return pathlib.Path("tests/files/cluster.png")


@pytest.fixture
def png_file(png_path):
    with png_path.open("rb") as f:
        yield f


@pytest.fixture
def file_identifier(store_root, pdf_path):
    p = store_root / "files" / "s/snakes.pdf"
    p.parent.mkdir(exist_ok=True, parents=True)
    shutil.copyfile(pdf_path, p)
    return "s/snakes.pdf"


@pytest.fixture()
def app(tagged_store, store_root):
    return helpers.create_app(
        tagged_store=tagged_store,
        store_root=store_root
    )


@pytest.fixture
def tagged_store():
    return MemoryTaggedObjectStore(initial_objects={})


@pytest.fixture
def file_manager(store_root):
    return FileManager(root=store_root)


@pytest.fixture
def document():
    return {
        "title": "a document with a title",
        "file_identifier": "1/1.pdf",
        "date_created": dt.datetime.now().isoformat()
    }
