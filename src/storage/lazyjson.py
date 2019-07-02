# -*- encoding: utf-8

import json
import os
import pathlib


class LazyJsonObject:
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
