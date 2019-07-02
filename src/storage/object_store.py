# -*- encoding: utf-8

import abc
import json
import pathlib

from .exceptions import AlreadyExistsError, NoSuchObject
from .lazyjson import LazyJsonObject


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

    def init(self, obj_id, *args, **kwargs):
        if obj_id in self.objects:
            raise AlreadyExistsError(obj_id)
        self.put(obj_id, *args, **kwargs)


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
        self.lazy_json = LazyJsonObject(path, cls=PosixPathEncoder)

    @property
    def path(self):
        return self.lazy_json.path

    @property
    def objects(self):
        return self.lazy_json.read()

    def put(self, obj_id, obj_data):
        if not isinstance(obj_id, str):
            raise TypeError(f"Expected type str, got {type(obj_id)}: {obj_id!r}")

        all_objects = self.objects
        all_objects[obj_id] = obj_data

        self.lazy_json.write(all_objects)
