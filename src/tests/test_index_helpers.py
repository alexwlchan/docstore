# -*- encoding: utf-8

import os
import subprocess

import pytest

from exceptions import UserError
import index_helpers
from tagged_store import TaggedDocument, TaggedDocumentStore


def create_thumbnail(monkeypatch, store, doc):
    def mock_subprocess(cmd):
        assert cmd == [
            "docker", "run", "--rm", "--volume", "%s:/data" % store.root,
            "preview-generator",
            "files/1/100.pdf", "thumbnails/%s/%s.jpg" % (doc.id[0], doc.id),
        ]

    with monkeypatch.context() as m:
        m.setattr(subprocess, "check_call", mock_subprocess)
        return index_helpers.create_thumbnail(store, doc)


def test_create_thumbnail(store, monkeypatch):
    doc = TaggedDocument({"id": "1", "pdf_path": "1/100.pdf"})
    create_thumbnail(monkeypatch, store=store, doc=doc)
    assert "thumbnail_path" in doc


def test_thumbnail_data_is_saved(store, monkeypatch):
    doc = TaggedDocument({"id": "1", "pdf_path": "1/100.pdf"})
    create_thumbnail(monkeypatch, store=store, doc=doc)

    new_store = TaggedDocumentStore(store.root)
    assert "thumbnail_path" in new_store.documents[doc.id]


def test_removes_old_thumbnail_first(store, monkeypatch):
    doc = TaggedDocument({
        "id": "1",
        "pdf_path": "1/100.pdf",
        "thumbnail_path": "1/100.jpg"
    })

    thumb_path = os.path.join(store.thumbnails_dir, doc["thumbnail_path"])
    os.makedirs(os.path.dirname(thumb_path))
    open(thumb_path, "wb").write(b"hello world")

    create_thumbnail(monkeypatch, store=store, doc=doc)
    assert not os.path.exists(thumb_path)
    assert doc["thumbnail_path"] != "1/100.jpg"


def test_copies_pdf_to_store(store, monkeypatch):
    user_data = {"path": "foo.pdf", "file": b"hello world"}
    doc = index_helpers.index_pdf_document(store=store, user_data=user_data)

    assert os.path.exists(os.path.join(store.files_dir, doc.id[0], doc.id + ".pdf"))
    assert doc["pdf_path"] == os.path.join(doc.id[0], doc.id + ".pdf")


def test_pdf_path_is_saved_to_store(store, monkeypatch):
    user_data = {"path": "foo.pdf", "file": b"hello world"}
    doc = index_helpers.index_pdf_document(store=store, user_data=user_data)

    new_store = TaggedDocumentStore(store.root)
    assert "pdf_path" in new_store.documents[doc.id]


def test_adds_sha256_hash_of_document(store, monkeypatch):
    user_data = {"path": "foo.pdf", "file": b"hello world"}
    doc = index_helpers.index_pdf_document(store=store, user_data=user_data)

    # sha256(b"hello world")
    assert (
        doc["sha256_checksum"] ==
        "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_leaves_correct_checksum_unmodified(store, monkeypatch):
    user_data = {
        "path": "foo.pdf",
        "file": b"hello world",

        # sha256(b"hello world")
        "sha256_checksum": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    }
    doc = index_helpers.index_pdf_document(store=store, user_data=user_data)

    assert doc["sha256_checksum"] == user_data["sha256_checksum"]


def test_raises_error_if_checksum_mismatch(store, monkeypatch):
    user_data = {"path": "foo.pdf", "file": b"hello world", "sha256_checksum": "123"}

    with pytest.raises(UserError, match="Incorrect SHA256 hash on upload"):
        index_helpers.index_pdf_document(store=store, user_data=user_data)
