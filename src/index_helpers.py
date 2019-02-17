# -*- encoding: utf-8

import os
import subprocess


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
