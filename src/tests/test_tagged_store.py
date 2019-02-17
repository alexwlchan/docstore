# -*- encoding: utf-8

import tempfile

import pytest

from tagged_store import TaggedDocumentStore


@pytest.fixture
def store():
    return TaggedDocumentStore(root=tempfile.mkdtemp())


def test_root_path_properties():
    store = TaggedDocumentStore("/foo")
    assert store.db_path == "/foo/documents.json"
    assert store.files_dir == "/foo/files"
    assert store.thumbs_dir == "/foo/thumbnails"


def test_gets_empty_documents_on_startup():
    store = TaggedDocumentStore("/foo")
    assert store.documents == []


def test_can_store_a_document(store):
    doc = {
        "id": "123",
        "tags": ["foo", "bar"]
    }
    store.index_document(doc)
    assert doc in store.documents


def test_documents_are_saved_to_disk(store):
    doc = {
        "id": "123",
        "tags": ["foo", "bar"]
    }
    store.index_document(doc)

    new_store = TaggedDocumentStore(root=store.root)
    assert doc in new_store.documents
