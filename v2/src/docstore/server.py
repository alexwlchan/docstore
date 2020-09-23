import collections
import os

from flask import Flask, jsonify, render_template, request, send_from_directory
import hyperlink

from docstore.files import get_documents


def create_app(root):
    app = Flask(__name__)

    @app.route('/')
    def list_documents():
        request_tags = set(request.args.getlist('tag'))
        documents = [
            doc
            for doc in get_documents(root)
            if request_tags.issubset(set(doc.tags))
        ]

        tag_tally = collections.Counter()
        for doc in documents:
            for t in doc.tags:
                tag_tally[t] += 1

        return render_template(
            'index.html',
            documents=sorted(documents, key=lambda d: d.date_created, reverse=True),
            request_tags=request_tags,
            request_url=hyperlink.DecodedURL.from_text(request.url),
            tag_tally=tag_tally
        )

    @app.route('/thumbnails/<shard>/<filename>')
    def thumbnails(shard, filename):
        return send_from_directory(
            os.path.abspath(os.path.join(root, 'thumbnails', shard)), filename=filename
        )

    @app.route('/files/<shard>/<filename>')
    def files(shard, filename):
        return send_from_directory(
            os.path.abspath(os.path.join(root, 'files', shard)), filename=filename
        )

    @app.template_filter('display_title')
    def display_title(document):
        parts = []
        if document.title is not None:
            parts.append(document.title)

        by_tags = [t[len('by:'):] for t in document.tags if t.startswith('by:')]
        if by_tags:
            parts.append('by %s' % ', '.join(by_tags))

        return ' '.join(parts)

    @app.template_filter('display_tags')
    def display_tags(document):
        return sorted(
            t for t in document.tags if not t.startswith('by:')
        )

    return app


def run_server(*, root, host, port, debug):
    app = create_app(root)
    app.run(host=host, port=port, debug=debug)
