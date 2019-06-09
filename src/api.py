#!/usr/bin/env python
# -*- encoding: utf-8

import json
import os
import pathlib
import urllib.parse
import uuid

import click
import hyperlink
from requests_toolbelt.multipart.decoder import NonMultipartContentTypeException
import responder
import scss
from whitenoise import WhiteNoise

import date_helpers
from exceptions import UserError
from file_manager import ThumbnailManager
from index_helpers import index_new_document
import search_helpers
from tagged_store import TaggedDocumentStore
from version import __version__


def prepare_form_data(user_data):
    prepared_data = {}

    # Copy across all the keys the app knows about.
    try:
        prepared_data["file"] = user_data.pop("file")
    except KeyError:
        raise UserError("Unable to find multipart upload 'file'!")

    # Handle HTML forms, which send this data as a dict of filename, content
    # and content-type.
    if isinstance(prepared_data["file"], dict):
        prepared_data["filename"] = prepared_data["file"]["filename"]
        prepared_data["file"] = prepared_data["file"]["content"]

    assert isinstance(prepared_data["file"], bytes), type(prepared_data["file"])

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
    if any(v for v in user_data.values()):
        prepared_data["user_data"] = {
            k: v.decode("utf8") for k, v in user_data.items() if v
        }

    return prepared_data


def create_api(store, display_title="Alex’s documents", default_view="table"):
    src_root = pathlib.Path(__file__).parent
    static_dir = src_root / "static"

    # Compile the CSS file before the API starts
    scss_path = src_root / "assets/style.scss"
    css = scss.Compiler().compile_string(scss_path.read_text())

    css_path = static_dir / "style.css"
    css_path.write_text(css)

    api = responder.API(
        static_dir=static_dir,
        templates_dir=src_root / "templates",
        version=__version__
    )

    api.static_url = lambda asset: "static/" + asset

    api.jinja_env.filters["since_now_date_str"] = date_helpers.since_now_date_str
    api.jinja_env.filters["short_url"] = lambda u: urllib.parse.urlparse(u).netloc
    api.jinja_env.filters["query_str_only"] = lambda url: "?" + "&".join(f"{k}={v}" for k, v in url.query)

    def add_headers_function(headers, path, url):
        # Add the Content-Disposition header to file requests, so they can
        # be downloaded with the original filename they were uploaded under
        # (if specified).
        #
        # For encoding as UTF-8, see https://stackoverflow.com/a/49481671/1558022
        doc_id, _ = os.path.splitext(os.path.basename(url))
        try:
            filename = store.underlying.objects[doc_id]["filename"]
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

    api.file_url = lambda doc: "files/" + str(doc["file_identifier"])

    whitenoise_thumbs = WhiteNoise(application=api._default_wsgi_app)
    whitenoise_thumbs.add_files(store.thumbnails_dir)
    api.mount("/thumbnails", whitenoise_thumbs)

    api.thumbnail_url = lambda doc: "thumbnails/" + str(doc["thumbnail_identifier"])

    @api.route("/")
    def list_documents(req, resp):
        tag_query = req.params.get_list("tag", [])
        sort_order = req.params.get("sort", "date_created:desc")
        view_option = req.params.get("view", default_view)

        search_options = search_helpers.SearchOptions(
            tag_query=tag_query,
            sort_order=tuple(sort_order.split(":"))
        )

        matching_documents = store.underlying.query(tag_query)

        sort_field, sort_order = tuple(sort_order.split(":"))
        display_documents = sorted(
            list(matching_documents.values()),
            key=lambda doc: doc.get(sort_field, ""),
            reverse=(sort_order == "desc")
        )

        tag_aggregation = search_helpers.get_tag_aggregation(display_documents)

        req_url = hyperlink.DecodedURL.from_text(req.full_url)

        params = {k: v for k, v in req.params.items()}
        try:
            params["_message"] = json.loads(params["_message"])
        except KeyError:
            pass

        resp.content = api.template(
            "document_list.html",
            search_options=search_options,
            display_documents=display_documents,
            tag_aggregation=tag_aggregation,
            view_option=view_option,
            title=display_title,
            req_url=req_url,
            params=params,
            cookies=req.cookies
        )

    @api.route("/documents/{document_id}")
    def individual_document(req, resp, *, document_id):
        try:
            resp.media = {
                k: (str(v) if isinstance(v, pathlib.Path) else v)
                for k, v in store.underlying.objects[document_id].items()
            }
        except KeyError:
            resp.media = {"error": "Document %s not found!" % document_id}
            resp.status_code = api.status_codes.HTTP_404

    @api.background.task
    def create_doc_thumbnail(doc_id, doc):
        thumbnail_manager = ThumbnailManager(root=store.thumbnails_dir)
        absolute_file_identifier = store.files_dir / doc["file_identifier"]

        doc["thumbnail_identifier"] = thumbnail_manager.create_thumbnail(
            doc_id,
            absolute_file_identifier
        )

        store.underlying.put(obj_id=doc_id, obj_data=doc)

        whitenoise_thumbs.add_file_to_dictionary(
            url="/" + str(doc["thumbnail_identifier"]),
            path=str(store.thumbnails_dir / doc["thumbnail_identifier"])
        )

    async def _upload_document_api(req, resp):
        if req.method == "post":

            # This catches the error that gets thrown if the user doesn't include
            # any files in their upload.
            try:
                user_data = await req.media(format="files")
            except NonMultipartContentTypeException as err:
                resp.media = {"error": str(err)}
                resp.status_code = api.status_codes.HTTP_400
                return

            doc_id = str(uuid.uuid4())

            try:
                prepared_data = prepare_form_data(user_data)
                doc = index_new_document(store=store, doc_id=doc_id, doc=prepared_data)
            except UserError as err:
                resp.media = {"error": str(err)}
                resp.status_code = api.status_codes.HTTP_400
                return

            whitenoise_files.add_file_to_dictionary(
                url="/" + str(doc["file_identifier"]),
                path=str(store.files_dir / doc["file_identifier"])
            )

            create_doc_thumbnail(doc_id=doc_id, doc=doc)

            resp.status_code = api.status_codes.HTTP_201
            resp.media = {"id": doc_id}
        else:
            resp.status_code = api.status_codes.HTTP_405

    @api.route("/upload")
    async def upload_document(req, resp):
        await _upload_document_api(req, resp)

        # If the request came through the browser rather than via
        # a script, redirect back to the original page (which we get
        # in the "referer" header), along with a message to display.
        try:
            original_url = hyperlink.URL.from_text(req.headers["referer"])
            new_url = original_url.add("_message", json.dumps(resp.media))
            resp.headers["Location"] = str(new_url)
            resp.status_code = api.status_codes.HTTP_302
        except KeyError:
            pass

    @api.route("/api/v1/recreate_thumbnails")
    async def recreate_thumbnails(req, resp):
        if req.method == "post":
            for doc_id, doc in store.underlying.objects.items():
                create_doc_thumbnail(doc_id=doc_id, doc=doc)

            resp.media = {"ok": "true"}
            resp.status_code = api.status_codes.HTTP_202
        else:
            resp.status_code = api.status_codes.HTTP_405

    return api


@click.command()
@click.version_option(version=__version__, prog_name="docstore")
@click.argument("root", required=True)
@click.option("--title", default="Alex’s documents")
@click.option("--default_view", default="table", type=click.Choice(["table", "grid"]))
def run_api(root, title, default_view):
    root = os.path.normpath(root)

    store = TaggedDocumentStore(root)
    api = create_api(store, display_title=title, default_view=default_view)

    api.run()


if __name__ == "__main__":  # pragma: no cover
    run_api()
