# -*- encoding: utf-8

import os
import pathlib
import random
import string


def safe_write(initial_path, data):
    """
    This method takes an initial filename and some bytes to write to that file,
    e.g.

        initial_path ~> "/documents/greeting.txt"
        data         ~> b"hello world"

    This function will write the data to that file, or a file with a similar name
    if the original path already exists.  It is thread-safe (so multiple processes
    writing to the same file won't collide).

    It returns the path to the file that was actually written.

    """
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
