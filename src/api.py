#!/usr/bin/env python
# -*- encoding: utf-8

import json
import multiprocessing
import pathlib
import sys
import urllib.parse
import uuid

from flask import Flask, jsonify, redirect, request
import gunicorn.app.base
import hyperlink
from whitenoise import WhiteNoise

import cli
import css
from exceptions import UserError
from file_manager import FileManager, ThumbnailManager
import index_helpers
import migrations
from pagination import Pagination
import search_helpers
from storage import JsonTaggedObjectStore
from version import __version__
import viewer


class Docstore:
    def __init__(self, tagged_store, config):
        self.tagged_store = tagged_store
        self.config = config

        self.app = Flask(__name__)

        # Configure Whitenoise to serve the large files statically, rather than
        # through the Flask server.
        # See http://whitenoise.evans.io/en/stable/flask.html
        self.app.wsgi_app = WhiteNoise(
            self.app.wsgi_app,
            add_headers_function=self._add_headers_function
        )

        for (static_dir, prefix) in [
            (config.root / "files", "/files"),
            (config.root / "thumbnails", "/thumbnails"),
            ("static", "/static"),
        ]:
            if pathlib.Path(static_dir).exists():
                self.whitenoise_app.add_files(static_dir, prefix=prefix)

        self.file_manager = FileManager(config.root / "files")
        self.thumbnail_manager = ThumbnailManager(config.root / "thumbnails")

        @self.app.route("/")
        def list_documents():
            return self._list_documents()

        @self.app.route("/documents/<doc_id>")
        def get_document(doc_id):
            try:
                retrieved_doc = tagged_store.objects[doc_id]
            except KeyError:
                return jsonify({"error": "Document %s not found!" % doc_id}), 404

            return jsonify({
                k: (str(v) if isinstance(v, pathlib.Path) else v)
                for k, v in retrieved_doc.items()
            })

        @self.app.route("/upload", methods=["POST"])
        def upload_document():
            resp, status_code = self._upload_document()

            if status_code != 201:
                return jsonify(resp), status_code

            # If the request came through the browser rather than via
            # a script, redirect back to the original page (which we get
            # in the "referer" header), along with a message to display.
            try:
                url = hyperlink.URL.from_text(request.headers["referer"])

                for key, value in resp.items():
                    url = url.add(f"_message.{key}", value)

                return redirect(location=str(url))
            except KeyError:
                pass

            return jsonify(resp), 201

    @property
    def whitenoise_app(self):
        return self.app.wsgi_app

    def _add_headers_function(self, headers, path, url):
        # Add the Content-Disposition header to file requests, so they can
        # be downloaded with the original filename they were uploaded under
        # (if specified).
        #
        # For encoding as UTF-8, see https://stackoverflow.com/a/49481671/1558022

        if url.startswith("/files/"):
            file_identifier = url.replace("/files/", "")

            try:
                # Because file identifiers are only ever a UUID or a slugified
                # value, we don't need to worry about weird encoding issues in URLs.
                matching_obj = [
                    obj
                    for obj in self.tagged_store.objects.values()
                    if str(obj["file_identifier"]) == file_identifier
                ][0]
                filename = matching_obj["filename"]
            except (IndexError, KeyError):
                pass
            else:
                encoded_filename = urllib.parse.quote(filename, encoding="utf-8")
                headers["Content-Disposition"] = f"filename*=utf-8''{encoded_filename}"

        headers["Cache-Control"] = "public, max-age=31536000"

    def _list_documents(self):
        tag_query = request.args.getlist("tag")

        page = int(request.args.get("page", "1"))
        page_size = int(request.args.get("page_size", "250"))

        matching_documents = self.tagged_store.query(tag_query)

        sort_param = request.args.get("sort", "date_created:newest_first")

        sort_options = {
            "title:a_z": ("title", False),
            "title:z_a": ("title", True),
            "date_created:oldest_first": ("date_created", False),
            "date_created:newest_first": ("date_created", True),
        }

        try:
            sort_field, sort_order_reverse = sort_options[sort_param]
        except KeyError:
            return jsonify({
                "error": f"Unrecognised sort parameter: {sort_param}"}), 400

        sorted_documents = sorted(
            matching_documents.values(),
            key=lambda doc: doc.get(sort_field, ""),
            reverse=sort_order_reverse
        )

        display_documents = sorted_documents

        tag_aggregation = search_helpers.get_tag_aggregation(display_documents)

        req_url = hyperlink.DecodedURL.from_text(request.url)

        params = {k: v for k, v in request.args.items()}
        try:
            params["_message"] = json.loads(params["_message"])
        except KeyError:
            pass

        view_options = viewer.ViewOptions(
            list_view=request.args.get("view", self.config.list_view),
            tag_view=self.config.tag_view,
            expand_document_form=(request.cookies.get('form-collapse__show') == 'true'),
            expand_tag_list=(request.cookies.get('tags-collapse__show') == 'true')
        )

        pagination = Pagination(
            page_size=page_size,
            current_page=page,
            total_documents=len(display_documents)
        )

        return viewer.render_document_list(
            documents=display_documents,
            tag_aggregation=tag_aggregation,
            view_options=view_options,
            tag_query=tag_query,
            title=self.config.title,
            req_url=req_url,
            accent_color=self.config.accent_color,
            pagination=pagination,
            api_version=__version__
        )

    def _upload_document(self):
        try:
            prepared_data = self._prepare_form_data()
        except UserError as err:
            return {"error": str(err)}, 400

        doc_id = str(uuid.uuid4())
        doc = index_helpers.index_new_document(
            self.tagged_store,
            self.file_manager,
            doc_id=doc_id,
            doc=prepared_data
        )

        self.whitenoise_app.add_file_to_dictionary(
            url=f"/files/{doc['file_identifier']}",
            path=str(self.file_manager.root / doc["file_identifier"])
        )

        try:
            self._create_doc_thumbnail(doc_id=doc_id, doc=doc)
        except Exception:
            pass

        return {"id": doc_id}, 201

    def _create_doc_thumbnail(self, doc_id, doc):
        absolute_file_identifier = self.file_manager.root / doc["file_identifier"]

        doc["thumbnail_identifier"] = self.thumbnail_manager.create_thumbnail(
            doc_id,
            absolute_file_identifier
        )

        self.tagged_store.put(obj_id=doc_id, obj_data=doc)

        self.whitenoise_app.add_file_to_dictionary(
            url=f"/thumbnails/{doc['thumbnail_identifier']}",
            path=str(self.thumbnail_manager.root / doc["thumbnail_identifier"])
        )

    @staticmethod
    def _prepare_form_data():
        known_keys = ("title", "tags")

        prepared_data = {
            key: request.form[key]
            for key in known_keys
            if key in request.form
        }

        try:
            prepared_data["tags"] = prepared_data["tags"].split()
        except KeyError:
            pass

        if any(k not in known_keys for k in request.form):
            prepared_data["user_data"] = {
                k: request.form[k]
                for k in request.form
                if k not in known_keys
            }

        try:
            uploaded_file = request.files["file"]
        except KeyError:
            raise UserError("No file in upload?")

        prepared_data["file"] = uploaded_file.read()
        prepared_data["filename"] = uploaded_file.filename

        return prepared_data


def run_api(config):  # pragma: no cover
    tagged_store = JsonTaggedObjectStore(config.root / "documents.json")

    migrations.apply_migrations(root=config.root, object_store=tagged_store)

    # Compile the CSS file before the API starts
    css.compile_css(accent_color=config.accent_color)

    docstore = Docstore(tagged_store, config=config)

    def number_of_workers():
        return (multiprocessing.cpu_count() * 2) + 1

    # From https://docs.gunicorn.org/en/stable/custom.html
    class StandaloneApplication(gunicorn.app.base.BaseApplication):

        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super(StandaloneApplication, self).__init__()

        def load_config(self):
            config = dict([(key, value) for key, value in self.options.items()
                           if key in self.cfg.settings and value is not None])
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        "bind": "0.0.0.0:8072",
        "workers": number_of_workers(),
    }

    StandaloneApplication(docstore.app.wsgi_app, options).run()


if __name__ == "__main__":  # pragma: no cover
    config = cli.parse_args(prog="docstore", version=__version__, argv=sys.argv[1:])
    run_api(config)
