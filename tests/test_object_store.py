# -*- encoding: utf-8

import abc
import contextlib
import json
import pathlib
import tempfile

import pytest

from storage import JsonObjectStore, MemoryObjectStore, NoSuchObject, ObjectStore


class ObjectStoreTestCasesMixin(abc.ABC):
    @abc.abstractmethod
    @contextlib.contextmanager
    def create_store(self, initial_objects):
        pass

    def test_can_get_objects(self):
        with self.create_store(initial_objects={"1": "one", "2": "two"}) as s:
            assert s.get(obj_id="1") == "one"
            assert s.get(obj_id="2") == "two"

            with pytest.raises(NoSuchObject):
                s.get(obj_id="3")

    def test_can_put_objects(self):
        with self.create_store(initial_objects={}) as s:
            s.put(obj_id="1", obj_data="one")

    def test_is_consistent(self):
        with self.create_store(initial_objects={}) as s:
            with pytest.raises(NoSuchObject):
                s.get(obj_id="1")

            s.put(obj_id="1", obj_data="one")
            assert s.get(obj_id="1") == "one"

            s.put(obj_id="1", obj_data="uno")
            assert s.get(obj_id="1") == "uno"


class TestMemoryObjectStore(ObjectStoreTestCasesMixin):
    @contextlib.contextmanager
    def create_store(self, initial_objects):
        yield MemoryObjectStore(initial_objects=initial_objects)


class TestJsonObjectStore(ObjectStoreTestCasesMixin):
    @contextlib.contextmanager
    def create_store(self, initial_objects):
        _, temp_path = tempfile.mkstemp()
        path = pathlib.Path(temp_path)
        path.write_text(json.dumps(initial_objects))

        yield JsonObjectStore(path)

        path.unlink()
