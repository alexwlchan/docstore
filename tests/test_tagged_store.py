# -*- encoding: utf-8

from tagged_store import TaggedDocumentStore


def test_root_path_properties(tmpdir):
    store = TaggedDocumentStore(root=tmpdir)
    assert store.files_dir == tmpdir.join("files")
    assert store.thumbnails_dir == tmpdir.join("thumbnails")


def test_creates_necessary_directories(tmpdir):
    store = TaggedDocumentStore(root=tmpdir)
    assert store.files_dir.exists()
    assert store.thumbnails_dir.exists()
