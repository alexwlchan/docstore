# -*- encoding: utf-8

import os

import pytest

from tagged_store import TaggedDocument, TaggedDocumentStore


def test_tagged_document_equality():
    d1 = TaggedDocument({"id": "1"})
    assert d1 == d1
    assert d1 == {"id": "1", "date_created": d1.date_created}


def test_tagged_document_inequality():
    d1 = TaggedDocument({"id": "1"})
    d2 = TaggedDocument({"id": "2"})
    assert d1 != d2


def test_tagged_document_inequality_with_other_types():
    d1 = TaggedDocument({"id": "1"})
    assert d1 != 2


def test_inconsistent_id_is_valuerror():
    with pytest.raises(ValueError, match=r"^IDs must match:"):
        TaggedDocument({"id": "1"}, doc_id="2")


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


def test_can_read_values():
    doc = TaggedDocument({"x": "xray"})
    assert doc["x"] == "xray"
    with pytest.raises(KeyError, match="y"):
        doc["y"]


def test_can_set_values():
    doc = TaggedDocument({"id": "1"})
    doc["foo"] = "bar"
    assert doc.data["foo"] == "bar"


def test_can_delete_value():
    doc = TaggedDocument({"foo": "bar"})
    del doc["foo"]
    with pytest.raises(KeyError, match="foo"):
        doc["foo"]


def test_doc_has_length():
    doc = TaggedDocument(data={})
    assert len(doc) == 1  # Created date
    doc["foo"] = "bar"
    doc["bar"] = "baz"
    assert len(doc) == 3


def test_can_iterate_over_doc():
    doc = TaggedDocument(data={})
    assert list(iter(doc)) == list(iter(doc.data))


def test_root_path_properties(tmpdir):
    root = str(tmpdir)
    store = TaggedDocumentStore(root)
    assert store.db_path == os.path.join(root, "documents.json")
    assert store.files_dir == os.path.join(root, "files")
    assert store.thumbnails_dir == os.path.join(root, "thumbnails")


def test_gets_empty_documents_on_startup(store):
    assert store.documents == {}


def test_can_store_a_document(store):
    doc = {"tags": ["foo", "bar"]}
    store.index_document(doc)
    assert doc in store.documents.values()


def test_documents_are_saved_to_disk(store):
    doc = {"tags": ["foo", "bar"]}
    store.index_document(doc)

    new_store = TaggedDocumentStore(root=store.root)
    assert store.documents == new_store.documents


def test_can_search_documents(store):
    doc1 = {"tags": ["foo", "bar"]}
    doc2 = {"tags": ["foo", "baz"]}
    doc3 = {"tags": []}

    store.index_document(doc1)
    store.index_document(doc2)
    store.index_document(doc3)

    assert store.search_documents(query=["foo"]) == [doc1, doc2]
    assert store.search_documents(query=["baz"]) == [doc2]
    assert store.search_documents(query=[]) == [doc1, doc2, doc3]


@pytest.mark.parametrize('doc', [object, None, 1, "foo"])
def test_indexing_a_non_taggeddocument_is_typeerror(store, doc):
    with pytest.raises(TypeError):
        store.index_document(doc)


def test_assigns_uuid_to_stored_document(store):
    doc = {"color": "red"}
    stored_doc = store.index_document(doc)

    print(stored_doc.id)


def test_can_update_document_by_uuid(store):
    doc = {"color": "blue"}
    stored_doc = store.index_document(doc)

    doc_new = {"id": stored_doc.id, "color": "red"}
    store.index_document(doc_new)

    assert len(store.documents) == 1
    assert doc not in store.documents.values()
    assert doc_new in store.documents.values()


def test_can_update_document_by_doc_id(store):
    doc = {"color": "green"}
    stored_doc = store.index_document(doc)

    doc_new = {"color": "yellow"}
    store.index_document(doc_new, doc_id=stored_doc.id)

    assert len(store.documents) == 1
    assert doc not in store.documents.values()
    assert doc_new in store.documents.values()


def test_creates_necessary_directories(store, tmpdir):
    store = TaggedDocumentStore(root=str(tmpdir))
    assert os.path.exists(store.files_dir)
    assert os.path.exists(store.thumbnails_dir)


def test_persists_id(tmpdir):
    store = TaggedDocumentStore(root=str(tmpdir))
    stored_doc = store.index_document({"name": "lexie"})

    new_store = TaggedDocumentStore(root=str(tmpdir))
    assert new_store.documents == {stored_doc.id: stored_doc}
    assert stored_doc.id == new_store.documents[stored_doc.id].id
