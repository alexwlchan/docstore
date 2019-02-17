# -*- encoding: utf-8

import filecmp
import os
import shutil
import subprocess

from tagged_store import TaggedDocument


def create_thumbnail(store, doc):
    try:
        os.unlink(os.path.join(store.thumbs_dir, doc.data["thumbnail_path"]))
    except KeyError:
        pass

    pdf_path = doc.data["pdf_path"]
    thumb_path = os.path.join(doc.id[0], doc.id + ".jpg")
    subprocess.check_call([
        "docker", "run", "--rm",
        "--volume", "%s:/data" % store.root,
        "preview-generator",
        os.path.join(store.files_dir, pdf_path).replace(store.root + "/", ""),
        os.path.join(store.thumbs_dir, thumb_path).replace(store.root + "/", ""),
    ])

    doc.data["thumbnail_path"] = thumb_path
    store.index_document(doc)


def index_pdf_document(store, user_data):
    path = user_data["path"]
    _, ext = os.path.splitext(path)
    if not ext.lower() == ".pdf":
        raise ValueError("path=%r does not point to a PDF!" % path)

    doc = TaggedDocument(user_data)

    pdf_path = os.path.join(doc.id[0], doc.id + ".pdf")
    complete_pdf_path = os.path.join(store.files_dir, pdf_path)
    os.makedirs(os.path.dirname(complete_pdf_path), exist_ok=True)
    shutil.copyfile(path, complete_pdf_path)
    doc.data["pdf_path"] = pdf_path

    # Store a copy before we create the thumbnail, so if the thumbnail creation
    # fails for some reason, we still have the document in the database.
    store.index_document(doc)

    create_thumbnail(store=store, doc=doc)

    # Once it's stored, we can clean up the original document.
    if not filecmp.cmp(path, complete_pdf_path):
        raise RuntimeError("PDF copy failed for %r!" % path)
    os.unlink(path)

    return doc

