import click

from docstore.server import run_server


@click.group()
def main():
    pass


@main.command(help="Run a docstore API server")
@click.option('--path', default='.', help='The root of the docstore database.', type=click.Path())
@click.option('--host', default='127.0.0.1', help='The interface to bind to.')
@click.option('--port', default=3391, help='The port to bind to.')
@click.option('--debug', default=False, is_flag=True, help='Run in debug mode.')
def serve(host, port, debug, path):
    run_server(path=path, host=host, port=port, debug=debug)
