# -*- encoding: utf-8

import hashlib


def sha256(f):
    h = hashlib.sha256()

    while True:
        next_buffer = f.read(65536)
        if not next_buffer:
            break
        h.update(next_buffer)

    return h.hexdigest()
