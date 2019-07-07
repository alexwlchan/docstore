# -*- encoding: utf-8

import os
import pathlib
import random
import string


def safe_write(initial_path, data):
    base, ext = os.path.splitext(initial_path)
    random_part = ""

    while True:
        path = pathlib.Path(base + random_part + ext)
        print(path)
        try:
            # Opening in exclusive write mode means we'll get an error if
            # the file already exists.
            with open(path, "xb") as outfile:
                outfile.write(data)
        except FileExistsError:
            random_part = "_" + "".join(
                random.choice(string.hexdigits) for _ in range(5))
        else:
            return path
