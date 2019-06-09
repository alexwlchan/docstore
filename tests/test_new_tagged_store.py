# -*- encoding: utf-8

import abc
import contextlib
import json
import pathlib
import tempfile

import pytest

from storage import JsonTaggedObjectStore, MemoryTaggedObjectStore


class TaggedObjectStoreTestCasesMixin(abc.ABC):
    @abc.abstractmethod
    @contextlib.contextmanager
    def create_store(self, initial_objects):
        pass

    @pytest.mark.parametrize("tag_query, expected_ids", [
        ([], {"apple", "banana", "cherry", "damson"}),
        ([1], {"apple", "banana"}),
        ([2], {"apple", "banana", "cherry"}),
        ([1, 4], set()),
        ([4], set()),
        ([2, 3], {"apple", "cherry"}),
    ])
    def test_can_perform_tag_query(self, tag_query, expected_ids):
        initial_objects = {
            "apple": {"tags": [1, 2, 3]},
            "banana": {"tags": [1, 2]},
            "cherry": {"tags": [2, 3]},
            "damson": {"tags": []},
        }

        with self.create_store(initial_objects) as s:
            assert s.query(tag_query).keys() == expected_ids


class TestMemoryObjectStore(TaggedObjectStoreTestCasesMixin):
    @contextlib.contextmanager
    def create_store(self, initial_objects):
        yield MemoryTaggedObjectStore(initial_objects=initial_objects)


class TestJsonObjectStore(TaggedObjectStoreTestCasesMixin):
    def temp_path(self):
        _, temp_path = tempfile.mkstemp()
        return pathlib.Path(temp_path)

    @contextlib.contextmanager
    def create_store(self, initial_objects):
        path = self.temp_path()
        path.write_text(json.dumps(initial_objects))

        yield JsonTaggedObjectStore(path)

        path.unlink()
