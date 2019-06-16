# -*- encoding: utf-8

from tagged_store import TaggedDocumentStore


def test_root_path_properties(store_root):
    store = TaggedDocumentStore(store_root)
    assert store.files_dir == store_root / "files"
    assert store.thumbnails_dir == store_root / "thumbnails"


def test_creates_necessary_directories(store_root):
    store = TaggedDocumentStore(store_root)
    assert store.files_dir.exists()
    assert store.thumbnails_dir.exists()
