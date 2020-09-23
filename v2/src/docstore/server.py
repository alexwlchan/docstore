import os

from flask import Flask, jsonify, render_template

from docstore.files import get_documents


def create_app(root):
    app = Flask(__name__)

    @app.route('/')
    def list_documents():
        documents = get_documents(root)
        return render_template('index.html', documents=documents)

    return app


def run_server(*, root, host, port, debug):
    app = create_app(root)
    app.run(host=host, port=port, debug=debug)
