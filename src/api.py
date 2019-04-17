#!/usr/bin/env python
# -*- encoding: utf-8

import os
import urllib.parse

import click
import hyperlink
from requests_toolbelt.multipart.decoder import NonMultipartContentTypeException
import responder
import scss
from whitenoise import WhiteNoise

import date_helpers
from exceptions import UserError
from index_helpers import create_thumbnail, index_document
import search_helpers
from tagged_store import TaggedDocumentStore
import urls
from version import __version__


def create_api(store, display_title="Alex’s documents"):
    # Compile the CSS file before the API starts
    css = scss.Compiler().compile_string(open("assets/style.scss").read())
    open("static/style.css", "w").write(css)

    api = responder.API(version=__version__)

    api.static_url = lambda asset: "static/" + asset

    api.jinja_env.filters["since_now_date_str"] = date_helpers.since_now_date_str
    api.jinja_env.filters["add_tag_to_url"] = urls.add_tag_to_url
    api.jinja_env.filters["remove_tag_from_url"] = urls.remove_tag_from_url
    api.jinja_env.filters["set_sort_order"] = urls.set_sort_order
    api.jinja_env.filters["set_view_option"] = urls.set_view_option

    def add_headers_function(headers, path, url):
        # Add the Content-Disposition header to file requests, so they can
        # be downloaded with the original filename they were uploaded under
        # (if specified).
        #
        # For encoding as UTF-8, see https://stackoverflow.com/a/49481671/1558022
        doc_id, _ = os.path.splitext(os.path.basename(url))
        try:
            filename = store.documents[doc_id].data["filename"]
        except KeyError:
            pass
        else:
            encoded_filename = urllib.parse.quote(filename, encoding="utf-8")
            headers["Content-Disposition"] = f"filename*=utf-8''{encoded_filename}"

    # Add routes for serving the static files/thumbnails
    whitenoise_files = WhiteNoise(
        application=api._default_wsgi_app,
        add_headers_function=add_headers_function
    )
    whitenoise_files.add_files(store.files_dir)
    api.mount("/files", whitenoise_files)

    api.file_url = lambda doc: "files/" + doc["file_identifier"]

    whitenoise_thumbs = WhiteNoise(application=api._default_wsgi_app)
    whitenoise_thumbs.add_files(store.thumbnails_dir)
    api.mount("/thumbnails", whitenoise_thumbs)

    api.thumbnail_url = lambda doc: "thumbnails/" + doc["thumbnail_identifier"]

    @api.route("/")
    def list_documents(req, resp):
        tag_query = req.params.get_list("tag", [])
        sort_order = req.params.get("sort", "date_created:desc")
        grid_view = req.params.get("view", "table") == "grid"

        search_options = search_helpers.SearchOptions(
            tag_query=tag_query,
            sort_order=tuple(sort_order.split(":"))
        )

        search_response = search_helpers.search_store(store, options=search_options)

        req_url = hyperlink.URL.from_text(req.full_url)

        resp.content = api.template(
            "document_list.html",
            search_options=search_options,
            search_response=search_response,
            grid_view=grid_view,
            title=display_title,
            req_url=req_url
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

    @api.route("/documents/{document_id}")
    def individual_document(req, resp, *, document_id):
        try:
            resp.media = store.documents[document_id].data
        except KeyError:
            resp.media = {"error": "Document %s not found!" % document_id}
            resp.status_code = api.status_codes.HTTP_404

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
                doc = index_document(store=store, user_data=prepared_data)
            except UserError as err:
                resp.media = {"error": str(err)}
                resp.status_code = api.status_codes.HTTP_400
                return

            @api.background.task
            def create_doc_thumbnail(doc):
                create_thumbnail(store=store, doc=doc)
                whitenoise_thumbs.add_file_to_dictionary(
                    url="/" + doc["thumbnail_identifier"],
                    path=os.path.join(store.thumbnails_dir, doc["thumbnail_identifier"])
                )

            whitenoise_files.add_file_to_dictionary(
                url="/" + doc["file_identifier"],
                path=os.path.join(store.files_dir, doc["file_identifier"])
            )

            create_doc_thumbnail(doc)
            resp.status_code = api.status_codes.HTTP_201
            resp.media = {"id": doc.id}
        else:
            resp.status_code = api.status_codes.HTTP_405

    return api


@click.command()
@click.version_option(version=__version__, prog_name="docstore")
@click.argument("root", required=True)
@click.option("--title", default="Alex’s documents")
def run_api(root, title):
    root = os.path.normpath(root)

    store = TaggedDocumentStore(root)
    api = create_api(store, display_title=title)

    api.run()


if __name__ == "__main__":  # pragma: no cover
    run_api()
