import datetime
import functools
import json
import os
import sys

import click


@click.group()
@click.option(
    "--root",
    default=".",
    help="The root of the docstore database.",
    type=click.Path(),
    show_default=True,
)
@click.pass_context
def main(ctx, root):
    ctx.obj = root


def _require_existing_instance(inner):
    """
    When you call ``docstore add``, most of the time you want to be adding
    documents to an existing instance, not creating a new instance.

    It's easy to get the directory wrong, so this decorator will check you
    really wanted to create a new instance vs. adding to an old one.
    """

    @functools.wraps(inner)
    def wrapper(*args, **kwargs):
        from docstore.documents import db_path

        root = click.get_current_context().obj

        if (
            root == "."
            and not os.path.exists(db_path("."))
            and not any(ag == "--root" or ag.startswith("--root=") for ag in sys.argv)
        ):  # pragma: no cover
            click.echo(
                f"There is no existing docstore instance at {os.path.abspath('.')}",
                err=True,
            )
            click.confirm("Do you want to create a new instance?", abort=True, err=True)

        return inner(*args, **kwargs)

    return wrapper


@main.command(help="Run a docstore API server")
@click.option(
    "--host", default="127.0.0.1", help="The interface to bind to.", show_default=True
)
@click.option("--port", default=3391, help="The port to bind to.", show_default=True)
@click.option("--title", default="", help="The title of the app.")
@click.option(
    "--thumbnail_width", default=200, help="Thumbnail width (px).", show_default=True
)
@click.option("--debug", default=False, is_flag=True, help="Run in debug mode.")
@click.option("--profile", default=False, is_flag=True, help="Run a profiler.")
@click.pass_obj
def serve(root, debug, profile, **kwargs):  # pragma: no cover
    from docstore.server import run_profiler, run_server

    if profile:
        run_profiler(root=root, **kwargs)
    else:
        run_server(root=root, debug=debug, **kwargs)


def _add_document(root, path, title, tags, source_url):
    tags = tags or ""
    tags = [t.strip() for t in tags.split(",") if t.strip()]

    title = title or ""

    from docstore.documents import store_new_document

    document = store_new_document(
        root=root,
        path=path,
        title=title,
        tags=tags,
        source_url=source_url,
        date_saved=datetime.datetime.now(),
    )

    print(document.id)


@main.command(help="Store a file in docstore")
@click.argument("path", nargs=1, type=click.Path(), required=True)
@click.option(
    "--title",
    help="The title of the file.",
    required=True,
    prompt="What is the title of the file?",
)
@click.option(
    "--tags",
    help="The tags to apply to the file.",
    required=True,
    prompt="How should the file be tagged?",
)
@click.option("--source_url", help="Where was this file downloaded from?.")
@click.pass_obj
@_require_existing_instance
def add(root, path, title, tags, source_url):
    return _add_document(
        root=root, path=path, title=title, tags=tags, source_url=source_url
    )


@main.command(help="Store a file on the web in docstore")
@click.option(
    "--url", help="URL of the file to store.", type=click.Path(), required=True
)
@click.option("--title", help="The title of the file.")
@click.option("--tags", help="The tags to apply to the file.")
@click.option("--source_url", help="Where was this file downloaded from?.")
@click.pass_obj
@_require_existing_instance
def add_from_url(root, url, title, tags, source_url):  # pragma: no cover
    from docstore.downloads import download_file

    path = download_file(url)

    return _add_document(
        root=root, path=path, title=title, tags=tags, source_url=source_url
    )


@main.command(help="Migrate a V1 docstore")
@click.option(
    "--v1_path",
    help="Path to the root of the V1 instance.",
    type=click.Path(),
    required=True,
)
@click.pass_obj
def migrate(root, v1_path):  # pragma: no cover
    documents = json.load(open(os.path.join(v1_path, "documents.json")))

    for _, doc in documents.items():
        stored_file_path = os.path.join(v1_path, "files", doc["file_identifier"])

        try:
            filename_path = os.path.join(v1_path, "files", doc["filename"])
        except KeyError:
            filename_path = stored_file_path

        if os.path.exists(stored_file_path):
            os.rename(stored_file_path, filename_path)

            from docstore.documents import store_new_document

            store_new_document(
                root=root,
                path=filename_path,
                title=doc.get("title", ""),
                tags=doc.get("tags", []),
                source_url=doc.get("user_data", {}).get("source_url", ""),
                date_saved=datetime.datetime.fromisoformat(doc["date_created"]),
            )
            print(doc.get("filename", os.path.basename(doc["file_identifier"])))


@main.command(help="Delete one or more documents")
@click.argument("doc_ids", nargs=-1)
@click.pass_obj
def delete(root, doc_ids):
    from docstore.documents import db_path, delete_document

    if not os.path.exists(db_path(root)):
        sys.exit(f"There is no docstore instance at {root}!")

    for d_id in doc_ids:
        delete_document(root=root, doc_id=d_id)
        print(d_id)


@main.command(help="Verify your stored files")
@click.pass_obj
def verify(root):
    import collections
    from docstore.documents import read_documents, sha256
    import tqdm

    errors = collections.defaultdict(list)

    for doc in tqdm.tqdm(list(read_documents(root))):
        for f in doc.files:
            f_path = os.path.join(root, f.path)
            if f.size != os.stat(f_path).st_size:
                errors[f.id].append(
                    f"Size mismatch\n  actual   = {os.stat(f_path).st_size}\n  expected = {f.size}"
                )

            if f.checksum != sha256(f_path):
                errors[f.id].append(
                    f"Checksum mismatch\n  actual   = {sha256(f_path)}\n  expected = {f.checksum}"
                )

    from pprint import pprint

    pprint(errors)


@main.command(help="Merge the files on two documents")
@click.argument("doc_ids", nargs=-1)
@click.option("--yes", is_flag=True, help="Skip confirmation prompts.")
@click.pass_obj
def merge(root, doc_ids, yes):
    if len(doc_ids) == 1:
        return

    from docstore.documents import read_documents

    documents = {d.id: d for d in read_documents(root)}

    documents_to_merge = [documents[d_id] for d_id in doc_ids]

    for doc in documents_to_merge:
        click.echo(
            f'{doc.id.split("-")[0]} {click.style(doc.title, fg="yellow") or "<untitled>"}'
        )

    if not yes:  # pragma: no cover
        click.confirm(f"Merge these {len(doc_ids)} documents?", abort=True)

    # What should the title of the merged document be?
    from docstore.merging import get_title_candidates

    title_candidates = get_title_candidates(documents_to_merge)

    if len(title_candidates) == 1:
        click.echo(f"Using common title: {click.style(title_candidates[0], fg='blue')}")
        new_title = title_candidates[0]
    else:
        print("")
        click.echo(f'Guessed title: {click.style(title_candidates[0], fg="blue")}')
        if yes or click.confirm("Use title?"):
            new_title = title_candidates[0]
        else:  # pragma: no cover
            new_title = click.edit("\n".join(title_candidates)).strip()

    # What should the tags on the merged document be?
    from docstore.merging import get_union_of_tags

    all_tags = get_union_of_tags(documents_to_merge)

    print("")

    if all(doc.tags == all_tags for doc in documents_to_merge):
        click.echo(f"Using common tags: {click.style(', '.join(all_tags), fg='blue')}")
        new_tags = all_tags
    else:
        click.echo(f"Guessed tags: {click.style(', '.join(all_tags), fg='blue')}")
        if yes or click.confirm("Use tags?"):
            new_tags = all_tags
        else:  # pragma: no cover
            new_tags = click.edit("\n".join(all_tags)).strip().splitlines()

    from docstore.documents import pairwise_merge_documents

    doc1 = documents[doc_ids[0]]
    for doc2_id in doc_ids[1:]:
        doc2 = documents[doc2_id]
        doc1 = pairwise_merge_documents(
            root=root, doc1=doc1, doc2=doc2, new_title=new_title, new_tags=new_tags
        )


def find_similar_pairs(tags, *, required_similarity=80):
    """
    Find pairs of similar-looking tags in the collection ``tags``.

    Increase ``required_similarity`` for stricter matching (=> less results).
    """
    import itertools

    from rapidfuzz import fuzz

    for t1, t2 in itertools.combinations(sorted(tags), 2):
        # utilities:gas, utilities:electricity
        if os.path.commonprefix([t1, t2]).endswith(":"):
            continue

        # utilities, utilities:gas
        if t1.startswith(f"{t2}:") or t2.startswith(f"{t1}:"):
            continue

        if fuzz.ratio(t1, t2) > required_similarity:
            yield (t1, t2)


@main.command(help="Show tags that might be similar")
@click.pass_obj
def show_similar_tags(root):
    import collections
    from docstore.documents import read_documents

    documents = read_documents(root)
    tags = collections.Counter()

    for doc in documents:
        for t in doc.tags:
            tags[t] += 1

    for t1, t2 in find_similar_pairs(set(tags)):
        print("%3d %s" % (tags[t1], t1))
        print("%3d %s" % (tags[t2], t2))
        print("")
