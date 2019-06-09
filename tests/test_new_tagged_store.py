# -*- encoding: utf-8

import abc
import contextlib
import json
import pathlib
import tempfile

import pytest

from storage import JsonTaggedObjectStore, MemoryTaggedObjectStore
from test_object_store import (
    ObjectStoreTestCasesMixin,
    TestJsonObjectStore,
    TestMemoryObjectStore
)


class TaggedObjectStoreTestCasesMixin(ObjectStoreTestCasesMixin):
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


class TestMemoryObjectStore(TaggedObjectStoreTestCasesMixin, TestMemoryObjectStore):
    @contextlib.contextmanager
    def create_store(self, initial_objects):
            yield MemoryTaggedObjectStore(initial_objects=initial_objects)


class TestJsonObjectStore(TaggedObjectStoreTestCasesMixin, TestJsonObjectStore):
    @contextlib.contextmanager
    def create_store(self, initial_objects):
        with super().create_store(initial_objects) as s:
            yield JsonTaggedObjectStore(s.path)
