#!/usr/bin/env python
# -*- encoding: utf-8

import contextlib
import errno
import os
import subprocess
import sys
import webbrowser

from requests_toolbelt.multipart.decoder import NonMultipartContentTypeException
import responder

import date_helpers
from exceptions import UserError
from index_helpers import index_pdf_document
import search_helpers
from tagged_store import TaggedDocumentStore


APP_PORT = 8072
NGINX_PORT = 8073


api = responder.API()

api.jinja_env.filters["since_now_date_str"] = date_helpers.since_now_date_str


@api.route("/")
def list_documents(req, resp):
    tag_query = req.params.get_list("tag", [])
    page = req.params.get("page", default=1)
    sort_order = req.params.get("sort", "_date_created:desc")

    search_options = search_helpers.SearchOptions(
        tag_query=tag_query,
        page=int(page),
        sort_order=tuple(sort_order.split(":"))
    )

    search_response = search_helpers.search_store(store, options=search_options)

    resp.content = api.template(
        "document_list.html",
        search_options=search_options,
        search_response=search_response,
        nginx_port=NGINX_PORT
    )


def process_upload_data(user_data):
    try:
        upload_file = user_data["file"]
    except KeyError:
        raise UserError("Unable to find multipart upload 'file'!")


@api.route("/upload")
async def upload_document(req, resp):
    if req.method == "post":
        resp.media = {"success": True}

        # This catches the error that gets thrown if the user doesn't include
        # any files in their upload.
        try:
            user_data = await req.media(format="files")
        except NonMultipartContentTypeException as err:
            resp.media = {"error": str(err)}
            resp.status_code = api.status_codes.HTTP_400
            return

        try:
            process_upload_data(user_data)
        except UserError as err:
            resp.media = {"error": str(err)}
            resp.status_code = api.status_codes.HTTP_400
            return

    else:
        resp.status_code = api.status_codes.HTTP_405


@api.route("/api/documents")
async def documents_endpoint(req, resp):
    if req.method == "post":
        user_data = await req.media(format="files")

        # @api.background.task
        def process_data(user_data):
            print(user_data)

            # We can't store 'bytes' in JSON without providing an encoding, so
            # turn them into str instances first.
            for k, v in user_data.items():
                if k != "file" and isinstance(v, bytes):
                    user_data[k] = v.decode("utf8")

            index_pdf_document(store=store, user_data=user_data)

            # make thumbnail creation a thing

        process_data(user_data)
        resp.media = {"success": True}
    else:
        resp.status_code = api.status_codes.HTTP_405


@contextlib.contextmanager
def run_nginx(root, nginx_port):
    subprocess.Popen([
        "docker", "run", "--rm",
        "--volume", "%s:/usr/share/nginx/html" % root,
        "--publish", "%s:80" % nginx_port,
        "nginx:alpine",
    ])
    yield


if __name__ == "__main__":
    try:
        root = os.path.normpath(sys.argv[1])
    except IndexError:
        root = os.path.join(os.environ["HOME"], "Documents", "docstore")

    store = TaggedDocumentStore(root)

    with run_nginx(root=root, nginx_port=NGINX_PORT):
        try:
            api.run(port=APP_PORT)
        except OSError as err:
            if err.errno == errno.EADDRINUSE:
                print("Server is already running!")
                webbrowser.open("http://localhost:%d" % APP_PORT)
            else:
                raise
