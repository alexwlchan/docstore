# -*- encoding: utf-8

import copy
import pathlib

from migrations import (
    replace_sha256_checksum_with_generic_field,
    add_missing_thumbnails,
)
from storage.object_store import MemoryObjectStore


class TestSha256ChecksumField:
    root = "test"

    def test_noop_if_no_checksum_field(self):
        store = MemoryObjectStore(initial_objects={
            "1": {"name": "alex"},
            "2": {"name": "lexie"}
        })

        replace_sha256_checksum_with_generic_field(self.root, object_store=store)

        assert store.objects == {
            "1": {"name": "alex"},
            "2": {"name": "lexie"}
        }

    def test_replaces_checksum_field(self):
        store = MemoryObjectStore(initial_objects={
            "1": {"name": "alex", "sha256_checksum": "abcdef"},
            "2": {"name": "lexie", "sha256_checksum": "ghijkl"}
        })

        replace_sha256_checksum_with_generic_field(self.root, object_store=store)

        assert store.objects == {
            "1": {"name": "alex", "checksum": "sha256:abcdef"},
            "2": {"name": "lexie", "checksum": "sha256:ghijkl"}
        }

    def test_does_not_overwrite_existing_checksum_field(self):
        store = MemoryObjectStore(initial_objects={
            "1": {"name": "alex", "sha256_checksum": "abcdef", "checksum": "xyz"},
            "2": {"name": "lexie", "sha256_checksum": "ghijkl"}
        })

        replace_sha256_checksum_with_generic_field(self.root, object_store=store)

        assert store.objects == {
            "1": {"name": "alex", "sha256_checksum": "abcdef", "checksum": "xyz"},
            "2": {"name": "lexie", "checksum": "sha256:ghijkl"}
        }

    def test_migration_is_atomic(self):
        count = [0]

        class CountingStore(MemoryObjectStore):
            def write(self, updated_objects):
                count[0] += 1
                return super().write(updated_objects)

        store = CountingStore(initial_objects={
            "1": {"name": "alex", "sha256_checksum": "abcdef"},
            "2": {"name": "lexie", "sha256_checksum": "ghijkl"}
        })

        replace_sha256_checksum_with_generic_field(self.root, object_store=store)

        assert count[0] == 1


class TestMissingThumbnailCreation:
    root = "test"

    def test_noop_if_thumbnail_present(self):
        initial_objects = {
            "1": {"thumbnail_identifier": "1/1.jpg", "file_identifier": "1/1.pdf"},
            "2": {"thumbnail_identifier": "2/2.jpg", "file_identifier": "2/2.pdf"}
        }

        store = MemoryObjectStore(initial_objects=copy.deepcopy(initial_objects))

        add_missing_thumbnails(self.root, object_store=store)

        assert store.objects == initial_objects

    def test_creates_missing_thumbnail(self, store_root, file_identifier):
        store = MemoryObjectStore(initial_objects={
            "1": {"file_identifier": file_identifier}
        })

        add_missing_thumbnails(root=store_root, object_store=store)

        assert store.objects == {
            "1": {
                "file_identifier": file_identifier,
                "thumbnail_identifier": pathlib.Path("1/1.jpeg")
            }
        }

    def test_skips_thumbnail_error(self, store_root):
        store = MemoryObjectStore(initial_objects={
            "1": {"file_identifier": "1/1.pdf"}
        })

        add_missing_thumbnails(root=store_root, object_store=store)

        assert store.objects == {
            "1": {"file_identifier": "1/1.pdf",}
        }
