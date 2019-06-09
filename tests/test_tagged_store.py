# -*- encoding: utf-8

from tagged_store import TaggedDocumentStore


def test_root_path_properties(tmpdir):
    store = TaggedDocumentStore(root=tmpdir)
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
