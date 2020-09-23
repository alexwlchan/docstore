import os

from flask import Flask, jsonify, render_template

from docstore.models import from_json


def _get_documents(db_path):
    try:
        with open(db_path) as infile:
            return from_json(infile.read)
    except FileNotFoundError:
        return []


def create_app(path):
    app = Flask(__name__)

    db_path = os.path.join(path, 'documents.json')

    @app.route('/')
    def list_documents():
        documents = _get_documents(db_path)
        return render_template('index.html', documents=documents)

    return app


def run_server(*, path, host, port, debug):
    app = create_app(path)
    app.run(host=host, port=port, debug=debug)
