# -*- encoding: utf-8

import pytest

from tagged_store import matches_tag_query, TaggedDocumentStore


@pytest.mark.parametrize('doc, query, expected_result', [
    ({"id": "1"}, [], True),
    ({"id": "2"}, ["apple"], False),
    ({"id": "3"}, ["apple", "banana"], False),
    ({"id": "4", "tags": []}, [], True),
    ({"id": "5", "tags": ["apple"]}, [], True),
    ({"id": "6", "tags": ["apple"]}, ["apple"], True),
    ({"id": "7", "tags": ["apple"]}, ["apple", "banana"], False),
    ({"id": "8", "tags": ["apple"]}, ["banana"], False),
])
def test_can_match_tag_query(doc, query, expected_result):
    assert matches_tag_query(doc, query) == expected_result


def test_root_path_properties(tmpdir):
    store = TaggedDocumentStore(root=tmpdir)
    assert store.db_path == tmpdir.join("documents.json")
    assert store.files_dir == tmpdir.join("files")
    assert store.thumbnails_dir == tmpdir.join("thumbnails")


def test_gets_empty_documents_on_startup(store):
    assert store.documents == {}


def test_can_store_a_document(store):
    doc = {"tags": ["foo", "bar"]}
    store.index_document(doc_id="1", doc=doc)
    assert doc in store.documents.values()


def test_documents_are_saved_to_disk(store):
    doc = {"tags": ["foo", "bar"]}
    store.index_document(doc_id="1", doc=doc)

    new_store = TaggedDocumentStore(root=store.root)
    assert store.documents == new_store.documents


def test_can_search_documents(store):
    doc1 = {"tags": ["foo", "bar"]}
    doc2 = {"tags": ["foo", "baz"]}
    doc3 = {"tags": []}

    store.index_document(doc_id="1", doc=doc1)
    store.index_document(doc_id="2", doc=doc2)
    store.index_document(doc_id="3", doc=doc3)

    assert store.search_documents(query=["foo"]) == [doc1, doc2]
    assert store.search_documents(query=["baz"]) == [doc2]
    assert store.search_documents(query=[]) == [doc1, doc2, doc3]


def test_can_update_document_by_id(store):
    doc = {"color": "blue"}
    store.index_document(doc_id="1", doc=doc)

    doc_new = {"color": "yellow"}
    store.index_document(doc_id="1", doc=doc_new)

    assert len(store.documents) == 1
    assert doc not in store.documents.values()
    assert doc_new in store.documents.values()


def test_creates_necessary_directories(tmpdir):
    store = TaggedDocumentStore(root=tmpdir)
    assert store.files_dir.exists()
    assert store.thumbnails_dir.exists()


def test_persists_id(tmpdir):
    store = TaggedDocumentStore(root=tmpdir)

    doc_id = "1"
    doc = {"name": "lexie"}

    store.index_document(doc_id=doc_id, doc=doc)

    new_store = TaggedDocumentStore(root=tmpdir)
    assert new_store.documents == {doc_id: doc}
