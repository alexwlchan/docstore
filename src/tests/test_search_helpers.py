# -*- encoding: utf-8

from search_helpers import search_store, SearchOptions, SearchResponse


def test_search_store_all(store):
    doc1 = {"id": 1, "tags": ["foo", "bar"]}
    doc2 = {"id": 2, "tags": ["foo", "baz"]}
    doc3 = {"id": 3, "tags": []}

    store.index_document(doc1)
    store.index_document(doc2)
    store.index_document(doc3)

    options = SearchOptions(tag_query=[])

    resp = search_store(store, options)
    assert isinstance(resp, SearchResponse)
    assert resp.documents == [doc1, doc2, doc3]
    assert resp.tags == {"foo": 2, "bar": 1, "baz": 1}
    assert resp.total == 3


def test_search_store_page(store):
    for i in range(5):
        doc1 = {"id": i * 3 + 1, "tags": ["foo", "bar"]}
        doc2 = {"id": i * 3 + 2, "tags": ["foo", "baz"]}
        doc3 = {"id": i * 3 + 3, "tags": []}

        store.index_document(doc1)
        store.index_document(doc2)
        store.index_document(doc3)

    options = SearchOptions(tag_query=[], page=2, page_size=3)

    resp = search_store(store, options)
    assert [doc["id"] for doc in resp.documents] == [4, 5, 6]
    assert resp.tags == {"foo": 10, "bar": 5, "baz": 5}
    assert resp.total == 15


def test_gets_tag_aggregation_based_on_query(store):
    for i in range(5):
        doc1 = {"id": i * 3 + 1, "tags": ["foo", "bar"]}
        doc2 = {"id": i * 3 + 2, "tags": ["foo", "baz"]}
        doc3 = {"id": i * 3 + 3, "tags": []}

        store.index_document(doc1)
        store.index_document(doc2)
        store.index_document(doc3)

    doc = {"id": 16, "tags": ["bar", "baz"]}
    store.index_document(doc)

    options = SearchOptions(tag_query=["bar"])

    resp = search_store(store, options)
    assert [doc["id"] for doc in resp.documents] == [1, 4, 7, 10, 13, 16]
    assert resp.tags == {"foo": 5, "bar": 6, "baz": 1}
    assert resp.total == 6


def test_respects_sort_order(store):
    docA = {"id": "a", "name": "apple"}
    docB = {"id": "b", "name": "banana"}
    docC = {"id": "c", "name": "cabbage"}
    docD = {"id": "d", "name": "damson"}

    store.index_document(docA)
    store.index_document(docC)
    store.index_document(docD)
    store.index_document(docB)

    options = SearchOptions(sort_order=("name", "asc"))
    resp = search_store(store, options)
    assert resp.documents == [docA, docB, docC, docD]

    options = SearchOptions(sort_order=("name", "desc"))
    resp = search_store(store, options)
    assert resp.documents == [docD, docC, docB, docA]

