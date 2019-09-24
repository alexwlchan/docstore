# -*- encoding: utf-8

import datetime as dt
import pathlib
import random
import shutil
import sys

import pytest

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
def app(store_root, tagged_store):
    docstore = api.Docstore(
        tagged_store=tagged_store,
        config=config.DocstoreConfig(
            root=store_root,
            title="test docstore instance",
            list_view=random.choice(["table", "grid"]),
            tag_view=random.choice(["list", "cloud"]),
            accent_color="#ff0000"
        )
    )

    # See https://flask.palletsprojects.com/en/1.1.x/testing/#the-testing-skeleton:
    #
    #   What [setting this flag] does is disable error catching during
    #   request handling, so that you get better error reports when performing
    #   test requests against the application.
    #
    docstore.app.config['TESTING'] = True

    return docstore.app.test_client()


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
