#!/usr/bin/env python
# -*- encoding: utf-8

import collections
import datetime as dt
import errno
import json
import os
import secrets
import shutil
import subprocess
import uuid
import webbrowser

import attr
import elasticsearch
from PIL import Image
import responder

import date_helpers
import search_helpers
from tagged_store import TaggedDocumentStore


api = responder.API()


def shard(filename):
    return os.path.join(filename[0].lower(), filename)


api.jinja_env.filters["since_now_date_str"] = date_helpers.since_now_date_str
api.jinja_env.filters["shard"] = shard


DOCSTORE_ROOT = os.path.join(os.environ["HOME"], "Documents", "docstore")

store = TaggedDocumentStore(DOCSTORE_ROOT)


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


def get_new_path(filename):
    shard_dir = os.path.join(DOCSTORE_DIR, filename[0].lower())
    os.makedirs(shard_dir, exist_ok=True)

    basename, ext = os.path.splitext(filename)
    new_path = os.path.join(shard_dir, filename)
    while True:
        if not os.path.exists(new_path):
            return new_path
        new_path = os.path.join(
            shard_dir,
            basename + "_" + secrets.token_hex(3) + ext
        )


def create_pdf_thumbnail(path):
    thumb_id = str(uuid.uuid4())
    thumb_path = os.path.join(DOCSTORE_THUMBS, thumb_id[0], thumb_id + ".jpg")
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)

    subprocess.check_call([
        "docker", "run", "--rm",
        "--volume", "%s:/data" % DOCSTORE_ROOT,
        "preview-generator",
        path.replace(DOCSTORE_ROOT + "/", ""),
        thumb_path.replace(DOCSTORE_ROOT + "/", "")
    ])

    return thumb_path.replace(DOCSTORE_THUMBS + "/", "")


@api.route("/api/documents")
async def documents_endpoint(req, resp):
    if req.method == "post":
        data = await req.media()

        doc_id = str(uuid.uuid4())

        @api.background.task
        def process_data(data):
            path = data["path"]
            filename = os.path.basename(path)

            _, ext = os.path.splitext(path)
            assert ext.lower() == ".pdf"

            new_path = get_new_path(filename)
            assert not os.path.exists(new_path)
            shutil.copyfile(path, new_path)

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

            doc["thumbnail_path"] = create_pdf_thumbnail(new_path)

            es_index.index_document(doc)

            existing_documents = json.load(open(DOCSTORE_DB))
            existing_documents.append(doc)
            json_string = json.dumps(existing_documents, indent=2, sort_keys=True)
            open(DOCSTORE_DB, "w").write(json_string)

            # Don't delete the original document until it's successfully indexed!
            os.unlink(path)

        process_data(data)
        resp.media = {"success": True, "id": doc_id}
    else:
        resp.status_code = api.status_codes.HTTP_405


@api.route("/api/rebuild_thumbnails")
async def rebuild_thumbnails(req, resp):
    if req.method != "post":
        resp.status_code = api.status_codes.HTTP_405
        return

    @api.background.task
    def rebuild_all_thumbnails():
        for doc in existing_documents:
            try:
                os.unlink(doc["thumbnail_path"])
            except (FileNotFoundError, KeyError):
                pass

            print(f"Recreating thumbnail for {doc['filename']}")
            doc["thumbnail_path"] = create_pdf_thumbnail(
                os.path.join(DOCSTORE_DIR, doc["filename"][0], doc["filename"])
            )

            es_index.index_document(doc)

            json_string = json.dumps(existing_documents, indent=2, sort_keys=True)
            open(DOCSTORE_DB, "w").write(json_string)

    rebuild_all_thumbnails()


if __name__ == "__main__":
    port = 8072

    try:
        api.run(port=port)
    except OSError as err:
        if err.errno == errno.EADDRINUSE:
            print("Server is already running!")
            webbrowser.open("http://localhost:%s" % port)
        else:
            raise
