# -*- encoding: utf-8

import json
import os
import pathlib


class LazyJsonObject:
    """
    This is a wrapper around a JSON file on disk that tries to balance speed
    and freshness.

    If the file hasn't changed, we don't need to reload it from disk.  Reads are
    (relatively) slow -- better to cache the contents in-memory.  But if the
    file changes under our feet, we need to pick up the changes.

    This isn't safe to use in a multi-threaded environment; writes might overlap
    with each other, but concurrent read should be fine.

    """
    def __init__(self, path, **encode_kwargs):
        self.path = pathlib.Path(path)
        self._encode_kwargs = encode_kwargs
        self._value = None
        self._fingerprint = None

    def _get_fingerprint(self):
        return os.stat(self.path)

    def _freshen(self):
        self._fingerprint = self._get_fingerprint()
        self._value = json.load(open(self.path))

    def read(self):
        if self._fingerprint != self._get_fingerprint():
            self._freshen()
        return self._value

    def write(self, value):
        json_string = json.dumps(
            value,
            indent=2,
            sort_keys=True,
            **self._encode_kwargs
        )

        # Write to the database atomically
        tmp_path = self.path.with_suffix(".json.tmp")
        tmp_path.write_text(json_string)
        tmp_path.rename(self.path)
