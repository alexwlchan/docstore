import collections
import datetime
import functools
import os
from urllib.parse import parse_qsl, urlparse, urlencode

from flask import Flask, render_template, request, send_from_directory
import smartypants
from werkzeug.middleware.profiler import ProfilerMiddleware

from docstore.documents import read_documents
from docstore.tag_cloud import TagCloud
from docstore.tag_list import render_tag_list
from docstore.text_utils import hostname, pretty_date


def tags_with_prefix(document, prefix):
    return [t for t in document.tags if t.startswith(prefix)]


def tags_without_prefix(document, prefix):
    return [t for t in document.tags if not t.startswith(prefix)]


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

        html = render_template(
            "index.html",
            documents=sorted(documents, key=lambda d: d.date_saved, reverse=True),
            request_tags=request_tags,
            query_string=tuple(parse_qsl(urlparse(request.url).query)),
            tag_tally=tag_tally,
            title=title,
            page=page,
            TagCloud=TagCloud,
        )

        return html

    @app.route("/thumbnails/<shard>/<filename>")
    def thumbnails(shard, filename):
        return send_from_directory(
            os.path.abspath(os.path.join(root, "thumbnails", shard)), filename=filename
        )

    @app.route("/files/<shard>/<filename>")
    def files(shard, filename):
        return send_from_directory(
            os.path.abspath(os.path.join(root, "files", shard)), filename=filename
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
