#!/usr/bin/env python
# -*- encoding: utf-8

import copy
import datetime as dt
import json
import os
import secrets
import subprocess
import time
import uuid

import elasticsearch
from PIL import Image
import requests
import responder

import date_helpers


api = responder.API()


def shard(filename):
    return os.path.join(filename[0].lower(), filename)


api.jinja_env.filters["since_now_date_str"] = date_helpers.since_now_date_str
api.jinja_env.filters["shard"] = shard


es = elasticsearch.Elasticsearch()


DOCSTORE_ROOT = os.path.join(os.environ["HOME"], "Documents", "docstore")

DOCSTORE_DB = os.path.join(DOCSTORE_ROOT, "documents.json")
DOCSTORE_DIR = os.path.join(DOCSTORE_ROOT, "files")
DOCSTORE_THUMBS = os.path.join(DOCSTORE_ROOT, "thumbnails")


index_name = ("documents" + dt.datetime.now().isoformat()).lower()


es.indices.create(
    index=index_name,
    body={
        "mappings": {
            "documents": {
                "properties": {
                    "indexed_at": {"type": "date"},
                    "tags": {"type": "keyword"},
                }
            }
        }
    }
)


try:
    existing_documents = json.load(open(DOCSTORE_DB))
except FileNotFoundError:
    os.makedirs(DOCSTORE_ROOT, exist_ok=True)

    with open(DOCSTORE_DB, "x") as outfile:
        outfile.write(json.dumps([]))

    existing_documents = []


def es_index_document(doc):
    enriched_doc = copy.deepcopy(doc)

    try:
        for t in enriched_doc["tags"]:
            while ":" in t:
                t, _ = t.rsplit(":", 1)
                if t not in enriched_doc["tags"]:
                    enriched_doc["tags"].append(t)
    except KeyError:
        pass

    es.index(
        index=index_name,
        doc_type="documents",
        id=enriched_doc["id"],
        body=enriched_doc
    )


for doc in existing_documents:
    es_index_document(doc)


def es_search_documents(index_name, tags=None, include_tag_aggs=False):
    body = {
        "sort": [
            {"indexed_at": {"order": "desc"}}
        ]
    }

    if include_tag_aggs:
        body["aggregations"] = {
            "tags": {
                "terms": {"field": "tags"}
            }
        }

    if tags:
        es_filter = {
            "bool": {
                "must": [
                    {"term": {"tags": t}} for t in tags
                ]
            }
        }
        body["query"] = {
            "bool": {"filter": es_filter}
        }

    return es.search(index=index_name, doc_type="documents", body=body)


@api.route("/")
def list_documents(req, resp):
    req_tags = req.params.get_list("tag", [])
    es_resp = es_search_documents(index_name, tags=req_tags, include_tag_aggs=True)
    resp.content = api.template(
        "document_list.html",
        documents=es_resp["hits"],
        req_tags=req_tags,
        all_tags={
            b["key"]: b["doc_count"]
            for b in es_resp["aggregations"]["tags"]["buckets"]
        }
    )


def get_new_path(filename):
    shard_dir = os.path.join(DOCSTORE_DIR, filename[0].lower())
    os.makedirs(shard_dir, exist_ok=True)

    basename, ext = os.path.splitext(filename)
    new_path = os.path.join(shard_dir, filename)
    while True:
        if not os.path.exists(new_path):
            return new_path
        new_path = os.path.join(shard_dir, basename + "_" + secrets.token_hex(3) + ext)


@api.route("/api/documents")
async def documents_endpoint(req, resp):
    if req.method == "get":
        es_resp = es_search_documents(index_name)
        docs = [hit["_source"] for hit in es_resp["hits"]["hits"]]
        resp.media = docs
    elif req.method == "post":
        data = await req.media()

        doc_id = str(uuid.uuid4())

        @api.background.task
        def process_data(data):
            path = data["path"]
            filename = os.path.basename(path)

            new_path = get_new_path(filename)
            assert not os.path.exists(new_path)
            os.rename(path, new_path)

            doc = {
                "id": doc_id,
                "filename": os.path.basename(new_path),
                "indexed_at": dt.datetime.now().isoformat(),
            }

            for extra_key in ("tags", "title",):
                try:
                    doc[extra_key] = data[extra_key]
                except KeyError:
                    pass

            thumb_path = new_path.replace(DOCSTORE_DIR, DOCSTORE_THUMBS)
            os.makedirs(os.path.dirname(thumb_path), exist_ok=True)

            _, ext = os.path.splitext(path)
            if ext == ".pdf":
                subprocess.check_call([
                    "docker", "run", "--rm",
                    "--volume", "%s:/files" % os.path.dirname(new_path),
                    "alexwlchan/imagemagick",
                    "convert",
                    "/files/%s[0]" % filename,
                    "/files/%s" % filename.replace(".pdf", ".jpg")
                ])
                new_path = new_path.replace(".pdf", ".jpg")

            try:
                im = Image.open(new_path)
            except OSError:
                pass
            else:
                im.thumbnail((60, 60))

                im.save(thumb_path)
                doc["has_thumbnail"] = True

            if ext == ".pdf":
                os.unlink(new_path)
                new_path = new_path.replace(".jpg", ".pdf")

            es_index_document(doc)

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
    api.run(port=8072)
