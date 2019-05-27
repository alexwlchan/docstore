# -*- encoding: utf-8

import collections

import attr


@attr.s
class SearchOptions:
    tag_query = attr.ib(default=())
    sort_order = attr.ib(default=("indexed_at", "desc"))


@attr.s
class SearchResponse:
    documents = attr.ib()
    tags = attr.ib()


def search_store(store, options):
    all_documents = store.search_documents(query=options.tag_query)

    tags = collections.defaultdict(int)
    for doc in all_documents:
        for t in doc.get("tags", []):
            tags[t] += 1

    sort_field, sort_order = options.sort_order
    all_documents.sort(
        key=lambda doc: doc.get(sort_field, ""),
        reverse=(sort_order == "desc")
    )

    return SearchResponse(
        documents=all_documents,
        tags=tags
    )
