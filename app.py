#!/usr/bin/env python
# -*- encoding: utf-8

import datetime as dt
import json
import os
import uuid

from elasticsearch import Elasticsearch
import responder

api = responder.API()

es = Elasticsearch()


DOCSTORE_ROOT = os.path.join(os.environ["HOME"], "Documents", "docstore")

DOCSTORE_DB = os.path.join(DOCSTORE_ROOT, "documents.json")


index_name = ("documents" + dt.datetime.now().isoformat()).lower()
print(index_name)


es.indices.create(index=index_name, ignore=400)

try:
    existing_documents = json.load(open(DOCSTORE_DB))
except FileNotFoundError:
    os.makedirs(DOCSTORE_ROOT, exist_ok=True)

    with open(DOCSTORE_DB, "x") as outfile:
        outfile.write(json.dumps([]))

    existing_documents = []


for doc in existing_documents:
    es.index(index=index_name, doc_type="documents", id=doc["id"], body=doc)


@api.route("/")
def list_documents(req, resp):
    es_resp = es.search(index=index_name, doc_type="documents")
    resp.content = api.template("document_list.html", documents=es_resp["hits"])


if __name__ == "__main__":
    api.run()
