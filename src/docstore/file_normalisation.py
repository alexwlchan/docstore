import os
import secrets
import shutil

from docstore.text_utils import slugify


def normalised_filename_copy(*, src, dst):
    """
    Copies a file from ``src`` to ``dst``.

    This rename function applies two normalisation steps:

    -   It removes non-ASCII characters and spaces
    -   It appends random hex value before the filename extension
        if there are multiple files with the same name

    This rename function tries to be "safe".  In particular, if there's
    already a file at ``dst``, it refuses to overwrite it.  Instead,
    it appends a random identifier to ``dst`` and copies to that instead.

    e.g. if you pass dst=``Statement.pdf``, it might create files like
    ``Statement.pdf``, ``Statement_1c5e.pdf``, ``Statement_3fc9.pdf``

    Returns the name of the final file.

    """
    out_dir, filename = os.path.split(dst)

    os.makedirs(out_dir, exist_ok=True)

    name, ext = os.path.splitext(filename)
    name = slugify(name)

    out_path = os.path.join(out_dir, name + ext)

    while True:
        try:
            with open(out_path, "xb") as out_file:
                with open(src, "rb") as infile:
                    shutil.copyfileobj(infile, out_file)
        except FileExistsError:
            out_path = os.path.join(out_dir, name + "_" + secrets.token_hex(2) + ext)
        else:
            return out_path
