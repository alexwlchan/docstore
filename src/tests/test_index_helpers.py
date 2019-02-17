# -*- encoding: utf-8

import os
import subprocess

import mock
import pytest

import index_helpers
from tagged_store import TaggedDocument, TaggedDocumentStore


def patched_create_thumbnail(monkeypatch, store, doc):
    def mock_subprocess(cmd):
        assert cmd == [
            "docker", "run", "--rm", "--volume", "%s:/data" % store.root,
            "preview-generator",
            "files/1/100.pdf", "thumbnails/%s/%s.jpg" % (doc.id[0], doc.id),
        ]

    with monkeypatch.context() as m:
        m.setattr(subprocess, "check_call", mock_subprocess)
        index_helpers.create_thumbnail(store, doc)


def test_create_thumbnail(store, monkeypatch):
    doc = TaggedDocument({"id": 1, "pdf_path": "1/100.pdf"})
    patched_create_thumbnail(monkeypatch, store=store, doc=doc)
    assert "thumbnail_path" in doc.data


def test_thumbnail_data_is_saved(store, monkeypatch):
    doc = TaggedDocument({"id": 1, "pdf_path": "1/100.pdf"})
    patched_create_thumbnail(monkeypatch, store=store, doc=doc)

    new_store = TaggedDocumentStore(store.root)
    assert "thumbnail_path" in new_store.documents[doc.id].data


def test_removes_old_thumbnail_first(store, monkeypatch):
    doc = TaggedDocument({
        "id": 1,
        "pdf_path": "1/100.pdf",
        "thumbnail_path": "1/100.jpg"
    })

    thumb_path = os.path.join(store.thumbs_dir, doc.data["thumbnail_path"])
    os.makedirs(os.path.dirname(thumb_path))
    open(thumb_path, "wb").write(b"hello world")

    patched_create_thumbnail(monkeypatch, store=store, doc=doc)
    assert not os.path.exists(thumb_path)
    assert doc.data["thumbnail_path"] != "1/100.jpg"


def test_indexing_non_pdf_is_error(store):
    user_data = {"path": "foo.jpg"}
    with pytest.raises(ValueError):
        index_helpers.index_pdf_document(store, user_data=user_data)


def test_copies_pdf_to_store(store):
    user_data = {"path": "tests/snakes.pdf"}
    doc = index_helpers.index_pdf_document(store, user_data=user_data)

    assert os.path.exists(os.path.join(store.files_dir, doc.id[0], doc.id + ".pdf"))
    assert doc.data["pdf_path"] == os.path.join(doc.id[0], doc.id + ".pdf")


def test_pdf_path_is_saved_to_store(store):
    user_data = {"path": "tests/snakes.pdf"}
    doc = index_helpers.index_pdf_document(store, user_data=user_data)

    new_store = TaggedDocumentStore(store.root)
    assert "pdf_path" in new_store.documents[doc.id].data
