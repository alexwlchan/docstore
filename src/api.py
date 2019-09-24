#!/usr/bin/env python
# -*- encoding: utf-8

import json
import sys
import urllib.parse

from flask import Flask, jsonify, redirect, request
import hyperlink
from whitenoise import WhiteNoise

import cli, css, index_helpers, migrations, search_helpers, viewer
from file_manager import FileManager, ThumbnailManager
from pagination import Pagination
from storage import JsonTaggedObjectStore
from version import __version__


class Docstore:
    def __init__(self, tagged_store, root, config):
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
            (root / "files", "/files"),
            (root / "thumbnails", "/thumbnails"),
            ("static", "/static"),
        ]:
            self.whitenoise_app.add_files(static_dir, prefix=prefix)

        self.file_manager = FileManager(root / "files")
        self.thumbnail_manager = ThumbnailManager(root / "thumbnails")

        @self.app.route("/")
        def list_documents():
            return self._list_documents()

        @self.app.route("/upload", methods=["POST"])
        def upload_document():
            resp = self._upload_document()

            # If the request came through the browser rather than via
            # a script, redirect back to the original page (which we get
            # in the "referer" header), along with a message to display.
            try:
                url = hyperlink.URL.from_text(request.headers["referer"])

                for key, value in resp.items():
                    url = url.add(f"_message.{key}", value)

                return redirect(
                    location=str(url),
                    response=resp
                )
            except KeyError:
                pass

            return 201, jsonify(resp)

    @property
    def whitenoise_app(self):
        return self.app.wsgi_app

    def _add_headers_function(self, headers, path, url):
        # Add the Content-Disposition header to file requests, so they can
        # be downloaded with the original filename they were uploaded under
        # (if specified).
        #
        # For encoding as UTF-8, see https://stackoverflow.com/a/49481671/1558022

        if path.startswith("files/"):
            file_identifier = path.replace("/files/", "")

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
        tag_query = request.args.getlist("tag", [])

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
            return 400, jsonify({
                "error": f"Unrecognised sort parameter: {sort_param}"})

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
            list_view=request.args.get("view", config.list_view),
            tag_view=config.tag_view,
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
            title=config.title,
            req_url=req_url,
            accent_color=config.accent_color,
            pagination=pagination,
            api_version=__version__
        )

    def _upload_document(self):
        # This catches the error that gets thrown if the user doesn't include
        # any files in their upload.
        try:
            user_data = request.files["file"]
        except NonMultipartContentTypeException as err:
            return 400, jsonify({"error": str(err)})

        doc_id = str(uuid.uuid4())

        try:
            prepared_data = self._prepare_form_data(user_data)
            doc = index_helpers.index_new_document(
                self.tagged_store,
                self.file_manager,
                doc_id=doc_id,
                doc=prepared_data
            )
        except UserError as err:
            resp.media = {"error": str(err)}
            resp.status_code = api.status_codes.HTTP_400
            return

        self.whitenoise_app.add_file_to_dictionary(
            url="/" + str(doc["file_identifier"]),
            path=str(file_manager.root / doc["file_identifier"])
        )

        try:
            self._create_doc_thumbnail(doc_id=doc_id, doc=doc)
        except Exception:
            pass

        return 201, jsonify({"id": doc_id})

    def _create_doc_thumbnail(self, doc_id, doc):
        absolute_file_identifier = self.file_manager.root / doc["file_identifier"]

        doc["thumbnail_identifier"] = self.thumbnail_manager.create_thumbnail(
            doc_id,
            absolute_file_identifier
        )

        self.tagged_store.put(obj_id=doc_id, obj_data=doc)

        self.whitenoise_app.add_file_to_dictionary(
            url="/" + str(doc["thumbnail_identifier"]),
            path=str(thumbnail_manager.root / doc["thumbnail_identifier"])
        )

    @staticmethod
    def _prepare_form_data(user_data):
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


def run_api(config):  # pragma: no cover
    tagged_store = JsonTaggedObjectStore(config.root / "documents.json")

    migrations.apply_migrations(root=config.root, object_store=tagged_store)

    # Compile the CSS file before the API starts
    css.compile_css(accent_color=config.accent_color)

    docstore = Docstore(tagged_store, root=config.root, config=config)

    docstore.app.run(port=8072, host="0.0.0.0", debug=True)


if __name__ == "__main__":  # pragma: no cover
    config = cli.parse_args(prog="docstore", version=__version__, argv=sys.argv[1:])
    run_api(config)
