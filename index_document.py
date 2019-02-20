#!/usr/bin/env python
# -*- encoding: utf-8

import click
import requests


@click.command()
@click.argument("path", required=True)
@click.option(
    "--tags", prompt="What is this document tagged with?", default=""
)
@click.option("--title", prompt="What is the title?", default="")
def main(path, title, tags):
    data = {
        "path": path
    }

    if title.strip():
        data["title"] = title.strip()

    if tags.split():
        data["tags"] = tags.split()

    resp = requests.post(
        "http://localhost:8072/api/documents",
        data=data,
        files={"file": open(path, "rb")}
    )
    resp.raise_for_status()
    print(resp.json())


if __name__ == "__main__":
    main()
