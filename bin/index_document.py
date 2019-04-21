#!/usr/bin/env python
# -*- encoding: utf-8

import os
import sys

import click
import requests


@click.command()
@click.argument("path", required=True)
@click.option("--port", default="8072")
@click.option(
    "--tags", prompt="What is this document tagged with?", default=""
)
@click.option("--title", prompt="What is the title?", default="")
@click.option("--source_url", prompt="What is the source URL?", default="")
@click.option("--cleanup", is_flag=True)
def main(path, port, title, source_url, tags, cleanup):
    url = "http://localhost:%s" % port

    data = {
        "filename": os.path.basename(path)
    }

    if title.strip():
        data["title"] = title.strip()

    if tags.split():
        data["tags"] = tags

    if source_url.strip():
        data["source_url"] = source_url.strip()

    resp = requests.post(
        url + "/upload",
        data=data,
        files={"file": open(path, "rb")}
    )
    resp.raise_for_status()
    print(resp.json())

    doc_id = resp.json()["id"]
    resp = requests.get(url + f"/documents/{doc_id}")
    resp.raise_for_status()

    url = os.path.join(url + "/files", resp.json()["file_identifier"])
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    stored_data = resp.raw.read()
    original_data = open(path, "rb").read()

    if stored_data != original_data:
        sys.exit("Saved file does not match original file!")

    if not cleanup:
        if click.confirm("File saved successfully.  Delete original file?"):
            os.unlink(path)


if __name__ == "__main__":
    main()
