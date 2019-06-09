# -*- encoding: utf-8

import abc

import pytest

from storage import MemoryObjectStore, NoSuchObject, ObjectStore


class ObjectStoreTestCasesMixin(abc.ABC):
    @abc.abstractmethod
    def create_store(self, initial_objects):
        pass

    def test_can_get_objects(self):
        s = self.create_store(initial_objects={1: "one", 2: "two"})
        assert s.get(obj_id=1) == "one"
        assert s.get(obj_id=2) == "two"

        with pytest.raises(NoSuchObject):
            s.get(obj_id=3)

    def test_can_put_objects(self):
        s = self.create_store(initial_objects={})
        s.put(obj_id=1, obj_data="one")

    def test_is_consistent(self):
        s = self.create_store(initial_objects={})

        with pytest.raises(NoSuchObject):
            s.get(obj_id=1)

        s.put(obj_id=1, obj_data="one")
        assert s.get(obj_id=1) == "one"

        s.put(obj_id=1, obj_data="uno")
        assert s.get(obj_id=1) == "uno"


class TestMemoryObjectStore(ObjectStoreTestCasesMixin):
    def create_store(self, initial_objects):
        return MemoryObjectStore(initial_objects=initial_objects)
