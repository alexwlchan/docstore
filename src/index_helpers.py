# -*- encoding: utf-8

import hashlib
import os
import subprocess

from tagged_store import TaggedDocument


def create_thumbnail(store, doc):
    try:
        os.unlink(os.path.join(store.thumbs_dir, doc.data["thumbnail_path"]))
    except KeyError:
        pass

    pdf_path = doc.data["pdf_path"]
    thumb_path = os.path.join(doc.id[0], doc.id + ".jpg")

    absolute_thumb_path = os.path.join(store.thumbs_dir, thumb_path)
    os.makedirs(os.path.dirname(absolute_thumb_path), exist_ok=True)

    subprocess.check_call([
        "docker", "run", "--rm",
        "--volume", "%s:/data" % store.root,
        "preview-generator",
        os.path.join(store.files_dir, pdf_path).replace(store.root + "/", ""),
        absolute_thumb_path.replace(store.root + "/", ""),
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
    open(complete_pdf_path, "wb").write(user_data.pop("file"))
    doc.data["pdf_path"] = pdf_path

    # Add a SHA256 hash of the PDF.  This allows integrity checking later
    # and makes it easy to detect duplicates.
    # Note: this slurps the entire PDF in at once.  Fine for small files;
    # might be worth revisiting if I ever get something unusually large.
    h = hashlib.sha256()
    h.update(open(complete_pdf_path, "rb").read())
    try:
        if doc.data["sha256_checksum"] != h.hexdigest():
            raise RuntimeError("Incorrect SHA256 hash on upload!")
    except KeyError:
        doc.data["sha256_checksum"] = h.hexdigest()

    # Store a copy before we create the thumbnail, so if the thumbnail creation
    # fails for some reason, we still have the document in the database.
    store.index_document(doc)

    create_thumbnail(store=store, doc=doc)

    return doc