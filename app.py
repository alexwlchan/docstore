#!/usr/bin/env python
# -*- encoding: utf-8

import datetime as dt
import json
import os
import uuid

import elasticsearch
from PIL import Image
import responder

api = responder.API()

es = elasticsearch.Elasticsearch()




DOCSTORE_ROOT = os.path.join(os.environ["HOME"], "Documents", "docstore")

DOCSTORE_DB = os.path.join(DOCSTORE_ROOT, "documents.json")
DOCSTORE_DIR = os.path.join(DOCSTORE_ROOT, "files")
DOCSTORE_THUMBS = os.path.join(DOCSTORE_ROOT, "thumbnails")


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


@api.route("/api/documents")
async def documents_endpoint(req, resp):
    if req.method == "get":
        es_resp = es.search(index=index_name, doc_type="documents")
        docs = [hit["_source"] for hit in es_resp["hits"]["hits"]]
        resp.media = docs
    elif req.method == "post":
        data = await req.media()

        doc_id = str(uuid.uuid4())

        @api.background.task
        def process_data(data):
            path = data["path"]
            filename = os.path.basename(path)

            shard_dir = os.path.join(DOCSTORE_DIR, filename[0].lower())
            os.makedirs(shard_dir, exist_ok=True)
            new_path = os.path.join(shard_dir, filename)
            os.rename(path, new_path)

            doc = {
                "id": doc_id,
                "filename": filename
            }

            _, ext = os.path.splitext(new_path)
            if ext.lower() in {".png",}:
                im = Image.open(new_path)
                im.thumbnail((60, 60))
                thumb_path = new_path.replace(DOCSTORE_DIR, DOCSTORE_THUMBS)
                os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                im.save(thumb_path)
                doc["has_thumbnail"] = True
            else:
                pass



            es.index(index=index_name, doc_type="documents", id=doc_id, body=doc)

            existing_documents = json.load(open(DOCSTORE_DB))
            existing_documents.append(doc)
            json_string = json.dumps(existing_documents, indent=2, sort_keys=True)
            open(DOCSTORE_DB, "w").write(json_string)

        process_data(data)
        resp.media = {"success": True, "id": doc_id}
    else:
        resp.status_code = api.status_codes.HTTP_405


@api.route("/api/documents/{doc_id}")
async def get_document(req, resp, *, doc_id):
    if req.method == "get":
        try:
            es_resp = es.get(index=index_name, doc_type="documents", id=doc_id)
        except elasticsearch.exceptions.NotFoundError:
            resp.status_code == api.status_codes.HTTP_404
        else:
            resp.media = es_resp["_source"]
    else:
        resp.status_code == api.status_codes.HTTP_405


if __name__ == "__main__":
    api.run()
