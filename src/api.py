#!/usr/bin/env python
# -*- encoding: utf-8

import errno
import os
import sys
import webbrowser

from requests_toolbelt.multipart.decoder import NonMultipartContentTypeException
import responder
from whitenoise import WhiteNoise

import date_helpers
from exceptions import UserError
from index_helpers import create_thumbnail, index_pdf_document
import search_helpers
from tagged_store import TaggedDocumentStore


APP_PORT = 8072


def create_api(store):
    api = responder.API()

    api.jinja_env.filters["since_now_date_str"] = date_helpers.since_now_date_str

    # Add routes for serving the static files/thumbnails
    whitenoise_files = WhiteNoise(application=api._default_wsgi_app)
    whitenoise_files.add_files(store.files_dir)
    api.mount("/files", whitenoise_files)

    whitenoise_thumbs = WhiteNoise(application=api._default_wsgi_app)
    whitenoise_thumbs.add_files(store.thumbnails_dir)
    api.mount("/thumbnails", whitenoise_thumbs)

    @api.route("/")
    def list_documents(req, resp):
        tag_query = req.params.get_list("tag", [])
        page = req.params.get("page", default=1)
        sort_order = req.params.get("sort", "date_created:desc")

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

    def prepare_upload_data(user_data):
        prepared_data = {}

        # Copy across all the keys the app knows about.
        try:
            prepared_data["file"] = user_data.pop("file")
        except KeyError:
            raise UserError("Unable to find multipart upload 'file'!")

        for key in ("title", "tags", "filename", "sha256_checksum"):
            try:
                prepared_data[key] = user_data.pop(key).decode("utf8")
            except KeyError:
                pass

        try:
            prepared_data["tags"] = prepared_data["tags"].split()
        except KeyError:
            pass

        # Any remaining keys we put into a special "user_data" array so they're
        # still saved, but don't conflict with other parameters we might add later.
        if user_data:
            prepared_data["user_data"] = {k: v.decode("utf8") for k, v in user_data.items()}

        return prepared_data

    @api.route("/upload")
    async def upload_document(req, resp):
        if req.method == "post":

            # This catches the error that gets thrown if the user doesn't include
            # any files in their upload.
            try:
                user_data = await req.media(format="files")
            except NonMultipartContentTypeException as err:
                resp.media = {"error": str(err)}
                resp.status_code = api.status_codes.HTTP_400
                return

            try:
                prepared_data = prepare_upload_data(user_data)
                doc = index_pdf_document(store=store, user_data=prepared_data)
            except UserError as err:
                resp.media = {"error": str(err)}
                resp.status_code = api.status_codes.HTTP_400
                return

            @api.background.task
            def create_doc_thumbnail(doc):
                create_thumbnail(store=store, doc=doc)

            create_doc_thumbnail(doc)
            resp.status_code = api.status_codes.HTTP_201
            resp.media = {"id": doc.id}
        else:
            resp.status_code = api.status_codes.HTTP_405

    return api


if __name__ == "__main__":  # pragma: no cover
    try:
        root = os.path.normpath(sys.argv[1])
    except IndexError:
        root = os.path.join(os.environ["HOME"], "Documents", "docstore")

    store = TaggedDocumentStore(root)
    api = create_api(store)

    try:
        api.run(port=APP_PORT)
    except OSError as err:
        if err.errno == errno.EADDRINUSE:
            print("Server is already running!")
            webbrowser.open("http://localhost:%d" % APP_PORT)
        else:
            raise
