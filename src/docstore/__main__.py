import datetime
import json
import os

import click

from docstore.files import pairwise_merge_documents, read_documents, store_new_document
from docstore.server import run_profiler, run_server
from docstore.text_utils import common_prefix


@click.group()
def main():
    pass


@main.command(help="Run a docstore API server")
@click.option(
    "--root",
    default=".",
    help="The root of the docstore database.",
    type=click.Path(),
    show_default=True,
)
@click.option(
    "--host", default="127.0.0.1", help="The interface to bind to.", show_default=True
)
@click.option("--port", default=3391, help="The port to bind to.", show_default=True)
@click.option("--debug", default=False, is_flag=True, help="Run in debug mode.")
@click.option("--profile", default=False, is_flag=True, help="Run a profiler.")
def serve(host, port, debug, root, profile):
    if profile:
        run_profiler(root=root, host=host, port=port)
    else:
        run_server(root=root, host=host, port=port, debug=debug)


@main.command(help="Store a file in docstore")
@click.option(
    "--root",
    default=".",
    help="The root of the docstore database.",
    type=click.Path(),
    show_default=True,
)
@click.option("--path", help="The file to store.", type=click.Path(), required=True)
@click.option("--title", help="The title of the file.")
@click.option("--tags", help="The tags to apply to the file.")
@click.option("--source_url", help="Where was this file downloaded from?.")
@click.option("--date_saved", help="When the file was saved in docstore.")
def add(root, path, title, tags, source_url, date_saved):
    tags = tags or ""
    tags = [t.strip() for t in tags.split(",") if t.strip()]

    title = title or ""

    if date_saved is not None:
        date_saved = datetime.datetime.fromisoformat(date_saved)
    else:
        date_saved = datetime.datetime.now()

    store_new_document(
        root=root,
        path=path,
        title=title,
        tags=tags,
        source_url=source_url,
        date_saved=date_saved,
    )


@main.command(help="Migrate a V1 docstore")
@click.option(
    "--root",
    default=".",
    help="The root of the docstore database.",
    type=click.Path(),
    show_default=True,
)
@click.option(
    "--v1_path",
    help="Path to the root of the V1 instance.",
    type=click.Path(),
    required=True,
)
def migrate(root, v1_path):
    documents = json.load(open(os.path.join(v1_path, "documents.json")))

    for _, doc in documents.items():
        stored_file_path = os.path.join(v1_path, "files", doc["file_identifier"])

        try:
            filename_path = os.path.join(v1_path, "files", doc["filename"])
        except KeyError:
            filename_path = stored_file_path

        if os.path.exists(stored_file_path):
            os.rename(stored_file_path, filename_path)
            store_new_document(
                root=root,
                path=filename_path,
                title=doc.get("title", ""),
                tags=doc["tags"],
                source_url=doc.get("user_data", {}).get("source_url", ""),
                date_created=datetime.datetime.fromisoformat(doc["date_created"]),
            )
            print(doc.get("filename", os.path.basename(doc["file_identifier"])))


@main.command(help="Merge the files on two documents")
@click.option(
    "--root",
    default=".",
    help="The root of the docstore database.",
    type=click.Path(),
    show_default=True,
)
@click.argument("doc_ids", nargs=-1)
def merge(root, doc_ids):
    if len(doc_ids) == 1:
        return

    documents = {d.id: d for d in read_documents(root)}

    for d_id in doc_ids:
        doc = documents[d_id]
        click.echo(f'{doc.id.split("-")[0]} {click.style(doc.title, fg="yellow") or "<untitled>"}')

    click.confirm(f'Merge these {len(doc_ids)} documents?', abort=True)

    # What should the title of the merged document be?
    title_candidates = []

    for d_id in doc_ids:
        doc = documents[d_id]
        if doc.title not in title_candidates:
            title_candidates.append(doc.title)

    guessed_title = common_prefix(title_candidates)

    print("")
    click.echo(f'Guessed title: {click.style(guessed_title, fg="blue")}')
    if click.confirm('Use title?'):
        new_title = guessed_title
    else:
        if guessed_title and guessed_title not in title_candidates:
            title_candidates.insert(0, guessed_title)

        new_title = click.edit('\n'.join(title_candidates)).strip()

    # What should the tags on the merged document be?
    tag_candidates = []
    all_tags = []

    for d_id in doc_ids:
        doc = documents[d_id]
        if doc.tags not in tag_candidates:
            tag_candidates.append(doc.tags)
        for t in doc.tags:
            if t not in all_tags:
                all_tags.append(t)

    # Every document has the same set of tags
    if len(tag_candidates) == 1:
        new_tags = tag_candidates[0]
    else:
        print("")
        click.echo(f"Guessed tags: {click.style(', '.join(all_tags), fg='blue')}")
        if click.confirm('Use title?'):
            new_tags = all_tags
        else:
            new_tags = click.edit('\n'.join(all_tags)).strip().splitlines()

    doc1 = documents[doc_ids[0]]
    for doc2_id in doc_ids[1:]:
        doc2 = documents[doc2_id]
        pairwise_merge_documents(
            root=root, doc1=doc1, doc2=doc2, new_title=new_title, new_tags=new_tags
        )
