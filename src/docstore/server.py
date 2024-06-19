import collections
import datetime
import functools
import hashlib
import os
import secrets
import urllib.parse
from urllib.parse import parse_qsl, urlparse, urlencode

from flask import (
    Flask,
    make_response,
    render_template,
    request,
    send_file,
    send_from_directory,
)
import hyperlink
import smartypants
from werkzeug.middleware.profiler import ProfilerMiddleware

from docstore.documents import find_original_filename, read_documents
from docstore.tag_cloud import TagCloud
from docstore.tag_list import render_tag_list
from docstore.text_utils import hostname, pretty_date


def tags_with_prefix(document, prefix):
    return [t for t in document.tags if t.startswith(prefix)]


def tags_without_prefix(document, prefix):
    return [t for t in document.tags if not t.startswith(prefix)]


def url_without_sortby(u):
    url = hyperlink.URL.from_text(u)
    return str(url.remove("sortBy"))


def serve_file(*, root, shard, filename):
    """
    Serves a file which has been saved in docstore.

    This adds the Content-Disposition header to the response, so files
    are downloaded with the original filename they were uploaded as,
    rather than the normalised filename.

    """
    path = os.path.abspath(os.path.join(root, "files", shard, filename))
    response = make_response(send_file(path))

    original_filename = find_original_filename(root, path=path)

    # See https://stackoverflow.com/a/49481671/1558022 for UTF-8 encoding
    encoded_filename = urllib.parse.quote(original_filename, encoding="utf-8")
    response.headers["Content-Disposition"] = f"filename*=utf-8''{encoded_filename}"

    return response


def create_app(title, root, thumbnail_width):
    app = Flask(__name__)

    app.config["THUMBNAIL_WIDTH"] = thumbnail_width

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    app.jinja_env.filters["hostname"] = hostname
    app.jinja_env.filters["pretty_date"] = lambda d: pretty_date(
        d, now=datetime.datetime.now()
    )
    app.jinja_env.filters["render_tag_list"] = render_tag_list
    app.jinja_env.filters["smartypants"] = smartypants.smartypants
    app.jinja_env.filters["url_without_sortby"] = url_without_sortby

    app.jinja_env.filters["tags_with_prefix"] = tags_with_prefix
    app.jinja_env.filters["tags_without_prefix"] = tags_without_prefix

    @app.route("/")
    def list_documents():
        request_tags = set(request.args.getlist("tag"))
        documents = [
            doc for doc in read_documents(root) if request_tags.issubset(set(doc.tags))
        ]

        tag_tally = collections.Counter()
        for doc in documents:
            for t in doc.tags:
                tag_tally[t] += 1

        try:
            page = int(request.args["page"])
        except KeyError:
            page = 1

        sort_by = request.args.get("sortBy", "date (newest first)")

        if sort_by.startswith("date"):
            sort_key = lambda d: d.date_saved  # noqa
        elif sort_by.startswith("title"):
            sort_key = lambda d: d.title.lower()  # noqa
        elif sort_by == "random":
            if page == 1:
                app.config["_RANDOM_SEED"] = secrets.token_bytes()
            seed = app.config["_RANDOM_SEED"]

            def sort_key(d):
                h = hashlib.md5()
                h.update(d.id.encode("utf8"))
                h.update(seed)
                return h.hexdigest()
        else:
            raise ValueError(f"Unrecognised sortBy query parameter: {sort_by}")

        if sort_by in {"date (newest first)", "title (Z to A)"}:
            sort_reverse = True
        else:
            sort_reverse = False

        html = render_template(
            "index.html",
            documents=sorted(documents, key=sort_key, reverse=sort_reverse),
            request_tags=request_tags,
            query_string=tuple(parse_qsl(urlparse(request.url).query)),
            tag_tally=tag_tally,
            title=title,
            page=page,
            sort_by=sort_by,
            TagCloud=TagCloud,
        )

        return html

    @app.route("/thumbnails/<shard>/<filename>")
    def thumbnails(shard, filename):
        return send_from_directory(
            os.path.abspath(os.path.join(root, "thumbnails", shard)), filename
        )

    app.add_url_rule(
        rule="/files/<shard>/<filename>",
        view_func=lambda shard, filename: serve_file(
            root=root, shard=shard, filename=filename
        ),
    )

    @app.template_filter("add_tag")
    @functools.lru_cache()
    def add_tag(query_string, tag):
        return "?" + urlencode(
            [(k, v) for k, v in query_string if k != "page"] + [("tag", tag)]
        )

    @app.template_filter("remove_tag")
    def remove_tag(query_string, tag):
        return "?" + urlencode(
            [(k, v) for k, v in query_string if (k, v) != ("tag", tag)]
        )

    @app.template_filter("set_page")
    @functools.lru_cache()
    def set_page(query_string, page):
        pageless_qs = [(k, v) for k, v in query_string if k != "page"]
        if page == 1:
            return "?" + urlencode(pageless_qs)
        else:
            return "?" + urlencode(pageless_qs + [("page", page)])

    return app


def run_profiler(*, host, port, **kwargs):  # pragma: no cover
    app = create_app(**kwargs)
    app.config["PROFILE"] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.run(host=host, port=port, debug=True)


def run_server(*, host, port, debug, **kwargs):  # pragma: no cover
    app = create_app(**kwargs)
    app.run(host=host, port=port, debug=debug)
