#!/usr/bin/env python
# -*- encoding: utf-8

import sys

import click
import requests


@click.command()
@click.option("--path", required=True)
@click.option("--title", prompt="What is the title?", default="")
@click.option("--tags", prompt="What is this document tagged with?", default="")
def main(path, title, tags):
    json = {
        "path": path
    }

    if title.strip():
        json["title"] = title.strip()

    if tags.split():
        json["tags"] = tags.split()

    resp = requests.post("http://localhost:8072/api/documents", json=json)
    resp.raise_for_status()
    print(resp.json())


if __name__ == "__main__":
    main()
