#!/usr/bin/env python
# -*- encoding: utf-8

import json
import os
import pathlib
import sys
import urllib.parse
import uuid

import hyperlink
from requests_toolbelt.multipart.decoder import NonMultipartContentTypeException
import responder
import scss
from whitenoise import WhiteNoise

import cli
from exceptions import UserError
from file_manager import FileManager, ThumbnailManager
from index_helpers import index_new_document
import migrations
import search_helpers
from storage import JsonTaggedObjectStore
import viewer
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

    for key in ("title", "tags", "filename"):
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


def compile_css(accent_color):
    src_root = pathlib.Path(__file__).parent
    static_dir = src_root / "static"

    # Compile the CSS file before the API starts
    from scss.namespace import Namespace
    from scss.types import Color
    namespace = Namespace()
    namespace.set_variable("$accent_color", Color.from_hex(accent_color))
    css = scss.Compiler(
        root=src_root / "assets",
        namespace=namespace).compile("style.scss")

    css_path = static_dir / "style.css"
    css_path.write_text(css)


def create_api(
    tagged_store,
    root,
    display_title="Alex’s documents",
    default_view="table",
    tag_view="list",
    accent_color="#007bff"
):
    file_manager = FileManager(root / "files")
    thumbnail_manager = ThumbnailManager(root / "thumbnails")

    src_root = pathlib.Path(__file__).parent
    static_dir = src_root / "static"

    api = responder.API(
        static_dir=static_dir,
        templates_dir=src_root / "templates",
        version=__version__
    )

    def add_headers_function(headers, path, url):
        # Add the Content-Disposition header to file requests, so they can
        # be downloaded with the original filename they were uploaded under
        # (if specified).
        #
        # For encoding as UTF-8, see https://stackoverflow.com/a/49481671/1558022
        file_identifier = "/".join(hyperlink.DecodedURL.from_text(url).path)

        try:
            # Because file identifiers are only ever a UUID or a slugified
            # value, we don't need to worry about weird encoding issues in URLs.
            matching_obj = [
                obj
                for obj in tagged_store.objects.values()
                if str(obj["file_identifier"]) == file_identifier
            ][0]
            filename = matching_obj["filename"]
        except (IndexError, KeyError):
            pass
        else:
            encoded_filename = urllib.parse.quote(filename, encoding="utf-8")
            headers["Content-Disposition"] = f"filename*=utf-8''{encoded_filename}"

        headers["Cache-Control"] = "public, max-age=31536000"

    # Add routes for serving the static files/thumbnails
    whitenoise_files = WhiteNoise(
        application=api._default_wsgi_app,
        add_headers_function=add_headers_function
    )

    if file_manager.root.exists():
        whitenoise_files.add_files(file_manager.root)

    api.mount("/files", whitenoise_files)

    def add_cache_control_headers(headers, path, url):
        headers["Cache-Control"] = "public, max-age=31536000"

    whitenoise_thumbs = WhiteNoise(
        application=api._default_wsgi_app,
        add_headers_function=add_cache_control_headers
    )

    if thumbnail_manager.root.exists():
        whitenoise_thumbs.add_files(thumbnail_manager.root)

    api.mount("/thumbnails", whitenoise_thumbs)

    @api.route("/")
    def list_documents(req, resp):
        tag_query = req.params.get_list("tag", [])
        sort_order = req.params.get("sort", "date_created:desc")

        search_options = search_helpers.SearchOptions(
            tag_query=tag_query,
            sort_order=tuple(sort_order.split(":"))
        )

        matching_documents = tagged_store.query(tag_query)

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

        view_options = viewer.ViewOptions(
            list_view=req.params.get("view", default_view),
            tag_view=tag_view,
            expand_document_form=(req.cookies.get('tags-collapse__show') == 'true'),
            expand_tag_list=(req.cookies.get('tags-collapse__show') == 'true')
        )

        resp.content = viewer.render_document_list(
            documents=display_documents,
            tag_aggregation=tag_aggregation,
            view_options=view_options,
            search_options=search_options,
            title=display_title,
            req_url=req_url,
            accent_color=accent_color,
            api_version=__version__
        )

    @api.route("/documents/{document_id}")
    def individual_document(req, resp, *, document_id):
        try:
            resp.media = {
                k: (str(v) if isinstance(v, pathlib.Path) else v)
                for k, v in tagged_store.objects[document_id].items()
            }
        except KeyError:
            resp.media = {"error": "Document %s not found!" % document_id}
            resp.status_code = api.status_codes.HTTP_404

    @api.background.task
    def create_doc_thumbnail(doc_id, doc):
        absolute_file_identifier = file_manager.root / doc["file_identifier"]

        doc["thumbnail_identifier"] = thumbnail_manager.create_thumbnail(
            doc_id,
            absolute_file_identifier
        )

        tagged_store.put(obj_id=doc_id, obj_data=doc)

        whitenoise_thumbs.add_file_to_dictionary(
            url="/" + str(doc["thumbnail_identifier"]),
            path=str(thumbnail_manager.root / doc["thumbnail_identifier"])
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
                doc = index_new_document(
                    tagged_store,
                    file_manager,
                    doc_id=doc_id,
                    doc=prepared_data
                )
            except UserError as err:
                resp.media = {"error": str(err)}
                resp.status_code = api.status_codes.HTTP_400
                return

            whitenoise_files.add_file_to_dictionary(
                url="/" + str(doc["file_identifier"]),
                path=str(file_manager.root / doc["file_identifier"])
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
            url = hyperlink.URL.from_text(req.headers["referer"])

            for key, value in resp.media.items():
                url = url.add(f"_message.{key}", value)

            resp.headers["Location"] = str(url)
            resp.status_code = api.status_codes.HTTP_302
        except KeyError:
            pass

    return api


def run_api(config):
    root = pathlib.Path(os.path.normpath(root))

    tagged_store = JsonTaggedObjectStore(config.root / "documents.json")

    migrations.apply_migrations(root=config.root, object_store=tagged_store)

    compile_css(accent_color=config.accent_color)

    api = create_api(
        tagged_store,
        root=config.root,
        display_title=config.title,
        default_view=config.list_view,
        tag_view=config.tag_view,
        accent_color=config.accent_color
    )

    api.run()


if __name__ == "__main__":  # pragma: no cover
    config = cli.parse_args(prog="docstore", version=__version__, argv=sys.argv)
    run_api(config)
