# -*- encoding: utf-8

import pytest

from tagged_store import TaggedDocument, TaggedDocumentStore


def test_tagged_document_equality():
    d1 = TaggedDocument({"id": "1"})
    assert d1 == d1
    assert d1 == {"id": "1"}
    assert d1 == TaggedDocument({"id": "1"})


def test_tagged_document_inequality():
    d1 = TaggedDocument({"id": "1"})
    d2 = TaggedDocument({"id": "2"})
    assert d1 != d2


def test_tagged_document_inequality_with_other_types():
    d1 = TaggedDocument({"id": "1"})
    assert d1 != 2


def test_cant_put_tagged_document_in_set():
    d1 = TaggedDocument({"id": "1"})
    with pytest.raises(TypeError, match=r"^unhashable type:"):
        set([d1])


@pytest.mark.parametrize('data, query, expected_result', [
    ({"id": "1"}, [], True),
    ({"id": "2"}, ["foo"], False),
    ({"id": "3"}, ["foo", "bar"], False),
    ({"id": "4", "tags": []}, [], True),
    ({"id": "5", "tags": ["foo"]}, [], True),
    ({"id": "6", "tags": ["foo"]}, ["foo"], True),
    ({"id": "7", "tags": ["foo"]}, ["foo", "bar"], False),
    ({"id": "8", "tags": ["foo"]}, ["bar"], False),
])
def test_can_match_tag_query(data, query, expected_result):
    doc = TaggedDocument(data)
    assert doc.matches_tag_query(query) == expected_result


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


def test_can_search_documents(store):
    doc1 = {"id": "1", "tags": ["foo", "bar"]}
    doc2 = {"id": "2", "tags": ["foo", "baz"]}
    doc3 = {"id": "3", "tags": []}

    store.index_document(doc1)
    store.index_document(doc2)
    store.index_document(doc3)

    assert store.search_documents(query=["foo"]) == [doc1, doc2]
    assert store.search_documents(query=["baz"]) == [doc2]
    assert store.search_documents(query=[]) == [doc1, doc2, doc3]
