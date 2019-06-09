# -*- encoding: utf-8

import abc

from .exceptions import NoSuchObject


class ObjectStore(abc.ABC):
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
        self._objects[obj_id] = obj_data
