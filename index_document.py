#!/usr/bin/env python
# -*- encoding: utf-8

import os

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
        "filename": os.path.basename(path)
    }

    if title.strip():
        data["title"] = title.strip()

    if tags.split():
        data["tags"] = tags

    resp = requests.post(
        "http://localhost:8072/upload",
        data=data,
        files={"file": open(path, "rb")}
    )
    resp.raise_for_status()
    print(resp.json())

    doc_id = resp.json()["id"]
    resp = requests.get(f"http://localhost:8072/documents/{doc_id}")
    resp.raise_for_status()

    url = os.path.join("http://localhost:8072/files", resp.json()["pdf_path"])
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    stored_data = resp.raw.read()
    original_pdf = open(path, "rb").read()

    if stored_data == original_pdf:
        os.unlink(path)


if __name__ == "__main__":
    main()
