#!/usr/bin/env python
# -*- encoding: utf-8

import os
import subprocess
import sys

import click


@click.command()
@click.argument("root", required=True)
@click.option("--port", default="8072")
@click.option("--title", default="Alex’s documents")
def run_docstore(root, port, title):
    cmd = [
        "docker", "run", "--rm",
        "--volume", "%s:/documents" % os.path.normpath(root),
        "--publish", "%s:%s" % (port, port),
        "--env", "PORT=%s" % port,
        "docstore",
        "--title", title
    ]

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as err:
        sys.exit(err.returncode)


if __name__ == "__main__":
    run_docstore()
