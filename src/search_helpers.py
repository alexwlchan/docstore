# -*- encoding: utf-8

import collections

import attr


@attr.s
class SearchOptions:
    tag_query = attr.ib(default=())
    page = attr.ib(default=1)
    page_size = attr.ib(default=48)
    sort_order = attr.ib(default=("indexed_at", "desc"))


@attr.s
class SearchResponse:
    documents = attr.ib()
    tags = attr.ib()
    total = attr.ib()


def search_store(store, options):
    all_documents = store.search_documents(query=options.tag_query)

    tags = collections.defaultdict(int)
    for doc in all_documents:
        for t in doc.tags:
            tags[t] += 1

    sort_field, sort_order = options.sort_order
    all_documents.sort(
        key=lambda doc: doc.data.get(sort_field, ""),
        reverse=(sort_order == "desc")
    )

    lower_page = options.page_size * (options.page - 1)
    upper_page = options.page_size * options.page

    documents_in_page = [doc.data for doc in all_documents[lower_page:upper_page]]

    return SearchResponse(
        documents=documents_in_page,
        tags=tags,
        total=len(all_documents)
    )
