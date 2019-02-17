#!/usr/bin/env python
# -*- encoding: utf-8

import errno
import os
import sys
import webbrowser

import responder

import date_helpers
from index_helpers import index_pdf_document
import search_helpers
from tagged_store import TaggedDocumentStore


api = responder.API()


api.jinja_env.filters["since_now_date_str"] = date_helpers.since_now_date_str


@api.route("/")
def list_documents(req, resp):
    tag_query = req.params.get_list("tag", [])
    page = req.params.get("page", default=1)
    sort_order = req.params.get("sort", "indexed_at:desc")

    search_options = search_helpers.SearchOptions(
        tag_query=tag_query,
        page=int(page),
        sort_order=tuple(sort_order.split(":"))
    )

    search_response = search_helpers.search_store(store, options=search_options)

    resp.content = api.template(
        "document_list.html",
        search_options=search_options,
        search_response=search_response
    )


@api.route("/api/documents")
async def documents_endpoint(req, resp):
    if req.method == "post":
        user_data = await req.media()

        @api.background.task
        def process_data(user_data):
            index_pdf_document(store=store, user_data=user_data)

        process_data(user_data)
        resp.media = {"success": True}
    else:
        resp.status_code = api.status_codes.HTTP_405


if __name__ == "__main__":
    port = 8072

    try:
        root = os.path.normpath(sys.argv[1])
    except IndexError:
        root = os.path.join(os.environ["HOME"], "Documents", "docstore")

    store = TaggedDocumentStore(root)

    try:
        api.run(port=port)
    except OSError as err:
        if err.errno == errno.EADDRINUSE:
            print("Server is already running!")
            webbrowser.open("http://localhost:%s" % port)
        else:
            raise
