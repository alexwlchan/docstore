#!/usr/bin/env python
# -*- encoding: utf-8

import datetime as dt
import json
import uuid

from elasticsearch import Elasticsearch
import responder

api = responder.API()

es = Elasticsearch()


index_name = ("documents" + dt.datetime.now().isoformat()).lower()
print(index_name)


es.indices.create(index=index_name, ignore=400)

es.index(
    index=index_name,
    doc_type="documents",
    id=str(uuid.uuid4()),
    body={
        "filename": "foo.pdf"
    }
)

es.index(
    index=index_name,
    doc_type="documents",
    id=str(uuid.uuid4()),
    body={
        "filename": "bar.pdf"
    }
)

es.index(
    index=index_name,
    doc_type="documents",
    id=str(uuid.uuid4()),
    body={
        "filename": "baz.pdf"
    }
)


@api.route("/")
def hello_world(req, resp):
    es_resp = es.search(index=index_name, doc_type="documents")
    print(es_resp)
    resp.content = api.template("document_list.html", documents=es_resp["hits"])


if __name__ == "__main__":
    api.run()
