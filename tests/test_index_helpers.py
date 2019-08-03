# -*- encoding: utf-8

import datetime as dt
import pathlib

import pytest

from exceptions import UserError
import index_helpers
from storage import AlreadyExistsError


def test_copies_pdf_to_store(tagged_store, file_manager, file_identifier, pdf_file):
    doc = {"path": file_identifier, "file": pdf_file.read()}
    doc_id = "1"
    index_helpers.index_new_document(tagged_store, file_manager, doc_id=doc_id, doc=doc)

    assert doc["file_identifier"] == pathlib.Path(doc_id[0]) / (doc_id + ".pdf")
    assert (file_manager.root / doc["file_identifier"]).exists()


def test_adds_sha256_hash_of_document(tagged_store, file_manager, file_identifier):
    doc = {"path": file_identifier, "file": b"hello world"}
    index_helpers.index_new_document(tagged_store, file_manager, doc_id="1", doc=doc)

    # sha256(b"hello world")
    assert (
        doc["sha256_checksum"] ==
        "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


@pytest.mark.parametrize('filename, extension', [
    ("bridge.jpg", ".jpg"),
    ("cluster.png", ".png"),
    ("snakes.pdf", ".pdf"),
])
def test_detects_correct_extension(tagged_store, file_manager, filename, extension):
    doc = {"file": (pathlib.Path("tests/files") / filename).read_bytes()}
    index_helpers.index_new_document(tagged_store, file_manager, doc_id="1", doc=doc)
    assert doc["file_identifier"].suffix == extension


def test_does_not_use_extension_if_cannot_detect_one(tagged_store, file_manager):
    doc = {
        "file": pathlib.Path("tests/files/metamorphosis.epub").read_bytes()
    }

    index_helpers.index_new_document(tagged_store, file_manager, doc_id="1", doc=doc)
    assert doc["file_identifier"].name == "1"


def test_uses_filename_if_cannot_detect_extension(tagged_store, file_manager):
    doc = {
        "file": pathlib.Path("tests/files/metamorphosis.epub").read_bytes(),
        "filename": "metamorphosis.epub"
    }

    index_helpers.index_new_document(tagged_store, file_manager, doc_id="1", doc=doc)
    assert doc["file_identifier"].suffix == ".epub"


def test_adds_created_date(tagged_store, file_manager):
    doc = {"file": b"hello world"}
    index_helpers.index_new_document(tagged_store, file_manager, doc_id="1", doc=doc)
    assert "date_created" in doc

    diff = (dt.datetime.now() - dt.datetime.strptime(doc["date_created"], "%Y-%m-%dT%H:%M:%S.%f"))
    assert diff.seconds < 5


def test_cannot_store_same_id_twice(tagged_store, file_manager):
    doc = {"file": b"hello world"}
    index_helpers.index_new_document(tagged_store, file_manager, doc_id="1", doc=doc)

    with pytest.raises(AlreadyExistsError):
        index_helpers.index_new_document(
            tagged_store,
            file_manager,
            doc_id="1",
            doc={"file": b"hello world"}
        )
