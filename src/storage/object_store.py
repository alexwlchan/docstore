# -*- encoding: utf-8

import abc
import json
import pathlib

from .exceptions import NoSuchObject


class ObjectStore(abc.ABC):
    """
    A store for serialising and storing arbitrary Python objects.

    Object IDs must be strings.  The store guarantees that you'll get an equal
    object back, but they may not be the same type.

    """

    @abc.abstractmethod
    def objects(self):
        pass

    def get(self, obj_id):
        try:
            return self.objects[obj_id]
        except KeyError as err:
            raise NoSuchObject(*err.args)

    @abc.abstractmethod
    def put(self, obj_id, obj_data):
        pass


class MemoryObjectStore(ObjectStore):
    def __init__(self, initial_objects):
        self._objects = initial_objects

    @property
    def objects(self):
        return self._objects

    def put(self, obj_id, obj_data):
        if not isinstance(obj_id, str):
            raise TypeError(f"Expected type str, got {type(obj_id)}: {obj_id!r}")
        self._objects[obj_id] = obj_data


class PosixPathEncoder(json.JSONEncoder):
    def default(self, obj):  # pragma: no cover
        if isinstance(obj, pathlib.Path):
            return str(obj)


class JsonObjectStore(ObjectStore):
    def __init__(self, path):
        self.path = path

        try:
            self._objects = json.load(self.path.open())
        except FileNotFoundError as err:
            self._objects = {}

    @property
    def objects(self):
        return self._objects

    def put(self, obj_id, obj_data):
        if not isinstance(obj_id, str):
            raise TypeError(f"Expected type str, got {type(obj_id)}: {obj_id!r}")

        updated_objects = self._objects.copy()
        updated_objects[obj_id] = obj_data

        json_string = json.dumps(
            updated_objects,
            indent=2,
            sort_keys=True,
            cls=PosixPathEncoder
        )

        # Write to the database atomically
        tmp_path = self.path.with_suffix(".json.tmp")
        tmp_path.write_text(json_string)
        tmp_path.rename(self.path)

        # Don't write to the in-memory database until it's been saved to disk
        self._objects = updated_objects
