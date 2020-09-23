import os

from flask import Flask, jsonify, render_template, send_from_directory

from docstore.files import get_documents


def create_app(root):
    app = Flask(__name__)

    @app.route('/')
    def list_documents():
        documents = get_documents(root)
        return render_template('index.html', documents=sorted(documents, key=lambda d: d.date_created, reverse=True))

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
        if document.title:
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
