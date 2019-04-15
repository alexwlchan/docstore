# -*- encoding: utf-8

import os

import pytest

from exceptions import UserError
import index_helpers
from tagged_store import TaggedDocument, TaggedDocumentStore


def test_create_thumbnail(store, file_identifier):
    doc = TaggedDocument({"id": "1", "file_identifier": file_identifier})
    index_helpers.create_thumbnail(store=store, doc=doc)
    assert "thumbnail_identifier" in doc


def test_thumbnail_data_is_saved(store, file_identifier):
    doc = TaggedDocument({"id": "1", "file_identifier": file_identifier})
    index_helpers.create_thumbnail(store=store, doc=doc)

    new_store = TaggedDocumentStore(store.root)
    assert "thumbnail_identifier" in new_store.documents[doc.id]


def test_removes_old_thumbnail_first(store, file_identifier):
    doc = TaggedDocument({
        "id": "1",
        "file_identifier": file_identifier,
        "thumbnail_identifier": "1/100.jpg"
    })

    thumb_path = os.path.join(store.thumbnails_dir, doc["thumbnail_identifier"])
    os.makedirs(os.path.dirname(thumb_path))
    open(thumb_path, "wb").write(b"hello world")

    index_helpers.create_thumbnail(store=store, doc=doc)
    assert not os.path.exists(thumb_path)
    assert doc["thumbnail_identifier"] != "1/100.jpg"


def test_copies_pdf_to_store(store, file_identifier, pdf_file):
    user_data = {"path": file_identifier, "file": pdf_file.read()}
    doc = index_helpers.index_document(store=store, user_data=user_data)

    assert doc["file_identifier"] == os.path.join(doc.id[0], doc.id + ".pdf")
    assert os.path.exists(os.path.join(store.files_dir, doc["file_identifier"]))


def test_adds_sha256_hash_of_document(store, file_identifier):
    user_data = {"path": file_identifier, "file": b"hello world"}
    doc = index_helpers.index_document(store=store, user_data=user_data)

    # sha256(b"hello world")
    assert (
        doc["sha256_checksum"] ==
        "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_leaves_correct_checksum_unmodified(store):
    user_data = {
        "path": "foo.pdf",
        "file": b"hello world",

        # sha256(b"hello world")
        "sha256_checksum": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    }
    doc = index_helpers.index_document(store=store, user_data=user_data)

    assert doc["sha256_checksum"] == user_data["sha256_checksum"]


def test_raises_error_if_checksum_mismatch(store):
    user_data = {"path": "foo.pdf", "file": b"hello world", "sha256_checksum": "123"}

    with pytest.raises(UserError, match="Incorrect SHA256 hash on upload"):
        index_helpers.index_document(store=store, user_data=user_data)


@pytest.mark.parametrize('filename,extension', [
    ("bridge.jpg", ".jpg"),
    ("cluster.png", ".png"),
    ("snakes.pdf", ".pdf"),
])
def test_detects_correct_extension(store, filename, extension):
    user_data = {"file": open(os.path.join("tests", "files", filename), "rb").read()}
    doc = index_helpers.index_document(store=store, user_data=user_data)
    assert doc["file_identifier"].endswith(extension)


# def test_errors_if_cannot_detect_extension(store):
#     user_data = {
#         "file": open(os.path.join("tests", "files", "metamorphosis.epub"), "rb").read()
#     }
#     index_document.index_document(store=store, user_data=user_data)
