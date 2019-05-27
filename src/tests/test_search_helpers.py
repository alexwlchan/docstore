# -*- encoding: utf-8

from search_helpers import search_store, SearchOptions, SearchResponse


def test_search_store_all(store):
    doc1 = {"tags": ["foo", "bar"]}
    doc2 = {"tags": ["foo", "baz"]}
    doc3 = {"tags": []}

    store.index_document(doc_id=1, doc=doc1)
    store.index_document(doc_id=2, doc=doc2)
    store.index_document(doc_id=3, doc=doc3)

    options = SearchOptions(tag_query=[])

    resp = search_store(store, options)
    assert isinstance(resp, SearchResponse)
    assert resp.documents == [doc1, doc2, doc3]
    assert resp.tags == {"foo": 2, "bar": 1, "baz": 1}


def test_gets_tag_aggregation_based_on_query(store):
    for i in range(5):
        doc1 = {"name": i * 3 + 1, "tags": ["foo", "bar"]}
        doc2 = {"name": i * 3 + 2, "tags": ["foo", "baz"]}
        doc3 = {"name": i * 3 + 3, "tags": []}

        store.index_document(doc_id=i * 3 + 1, doc=doc1)
        store.index_document(doc_id=i * 3 + 2, doc=doc2)
        store.index_document(doc_id=i * 3 + 3, doc=doc3)

    doc = {"name": 16, "tags": ["bar", "baz"]}
    store.index_document(doc_id=16, doc=doc)

    options = SearchOptions(tag_query=["bar"])

    resp = search_store(store, options)
    assert [doc["name"] for doc in resp.documents] == [1, 4, 7, 10, 13, 16]
    assert resp.tags == {"foo": 5, "bar": 6, "baz": 1}


def test_respects_sort_order(store):
    docA = {"name": "apple"}
    docB = {"name": "banana"}
    docC = {"name": "cabbage"}
    docD = {"name": "damson"}

    store.index_document(doc_id="a", doc=docA)
    store.index_document(doc_id="c", doc=docC)
    store.index_document(doc_id="d", doc=docD)
    store.index_document(doc_id="b", doc=docB)

    options = SearchOptions(sort_order=("name", "asc"))
    resp = search_store(store, options)
    assert resp.documents == [docA, docB, docC, docD]

    options = SearchOptions(sort_order=("name", "desc"))
    resp = search_store(store, options)
    assert resp.documents == [docD, docC, docB, docA]
