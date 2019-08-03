# -*- encoding: utf-8

from migrations import replace_sha256_checksum_with_generic_field
from storage.object_store import MemoryObjectStore


class TestSha256ChecksumField:
    def test_noop_if_no_checksum_field(self):
        store = MemoryObjectStore(initial_objects={
            "1": {"name": "alex"},
            "2": {"name": "lexie"}
        })

        replace_sha256_checksum_with_generic_field(store)

        assert store.objects == {
            "1": {"name": "alex"},
            "2": {"name": "lexie"}
        }

    def test_replaces_checksum_field(self):
        store = MemoryObjectStore(initial_objects={
            "1": {"name": "alex", "sha256_checksum": "abcdef"},
            "2": {"name": "lexie", "sha256_checksum": "ghijkl"}
        })

        replace_sha256_checksum_with_generic_field(store)

        assert store.objects == {
            "1": {"name": "alex", "checksum": "sha256:abcdef"},
            "2": {"name": "lexie", "checksum": "sha256:ghijkl"}
        }

    def test_does_not_overwrite_existing_checksum_field(self):
        store = MemoryObjectStore(initial_objects={
            "1": {"name": "alex", "sha256_checksum": "abcdef", "checksum": "xyz"},
            "2": {"name": "lexie", "sha256_checksum": "ghijkl"}
        })

        replace_sha256_checksum_with_generic_field(store)

        assert store.objects == {
            "1": {"name": "alex", "sha256_checksum": "abcdef", "checksum": "xyz"},
            "2": {"name": "lexie", "checksum": "sha256:ghijkl"}
        }
