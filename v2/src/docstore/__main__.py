import datetime

import click

from docstore.files import store_new_document
from docstore.server import run_server


@click.group()
def main():
    pass


@main.command(help="Run a docstore API server")
@click.option('--root', default='.', help='The root of the docstore database.', type=click.Path(), show_default=True)
@click.option('--host', default='127.0.0.1', help='The interface to bind to.', show_default=True)
@click.option('--port', default=3391, help='The port to bind to.', show_default=True)
@click.option('--debug', default=False, is_flag=True, help='Run in debug mode.')
def serve(host, port, debug, root):
    run_server(root=root, host=host, port=port, debug=debug)


@main.command(help="Store a file in docstore")
@click.option('--root', default='.', help='The root of the docstore database.', type=click.Path(), show_default=True)
@click.option('--path', help='The file to store.', type=click.Path(), required=True)
@click.option('--title', help='The title of the file.')
@click.option('--tags', help='The tags to apply to the file.')
@click.option('--source_url', help='Where was this file downloaded from?.')
@click.option('--date_created', help='When the file was created in docstore.')
def add(root, path, title, tags, source_url, date_created):
    tags = tags or ''
    tags = [t.strip() for t in tags.split(',') if t.strip()]

    title = title or ''

    if date_created is not None:
        date_created = datetime.datetime.fromisoformat(date_created)
    else:
        date_created = datetime.datetime.now()

    store_new_document(
        root=root, path=path, title=title, tags=tags, source_url=source_url, date_created=date_created
    )
