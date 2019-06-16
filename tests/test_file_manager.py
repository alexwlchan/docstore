# -*- encoding: utf-8

import abc
import os
import pathlib

import pytest

from file_manager import FileManager, ThumbnailManager


class FileManagerTestMixin(abc.ABC):

    @abc.abstractmethod
    def create_manager(self, store_root):
        return NotImplemented

    def test_shards_filenames(self, store_root):
        manager = self.create_manager(store_root)
        resp = manager.write_bytes(file_id="1234", buffer=b"hello world")
        assert resp.parent == pathlib.Path("1")
        assert str(resp).startswith("1/1234")

    def test_writes_bytes_to_disk(self, store_root):
        manager = self.create_manager(store_root)
        resp = manager.write_bytes(file_id="1234", buffer=b"hello world")
        assert (manager.root / resp).read_bytes() == b"hello world"

    def test_creates_intermediate_directories(self, store_root):
        root = store_root / "1/2/3"
        manager = FileManager(root)

        resp = manager.write_bytes(file_id="1234", buffer=b"hello world")
        assert (manager.root / resp).read_bytes() == b"hello world"

    @pytest.mark.parametrize("filename, expected_extension", [
        ("example.jpg", ".jpg"),
        ("document.pdf", ".pdf"),
        ("data.txt", ".txt"),
    ])
    def test_uses_filename_extension_if_present(
        self, store_root, filename, expected_extension
    ):
        manager = self.create_manager(store_root)
        resp = manager.write_bytes(
            file_id="1234", buffer=b"hello world", original_filename=filename
        )
        assert resp.suffix == expected_extension

    def test_detects_file_extension(self, store_root):
        manager = self.create_manager(store_root)
        png_data = pathlib.Path("tests/files/cluster.png").read_bytes()
        resp = manager.write_bytes(file_id="1234", buffer=png_data)
        assert resp.suffix == ".png"

    def test_no_extension_if_it_cannot_detect_one(self, store_root):
        manager = self.create_manager(store_root)
        epub_data = pathlib.Path("tests/files/metamorphosis.epub").read_bytes()
        resp = manager.write_bytes(file_id="1234", buffer=epub_data)
        assert resp.suffix == ""

    def test_uses_correct_jpeg_extension(self, store_root):
        manager = self.create_manager(store_root)
        jpg_data = pathlib.Path("tests/files/bridge.jpg").read_bytes()
        resp = manager.write_bytes(file_id="1234", buffer=jpg_data)
        assert resp.suffix == ".jpg"

    @pytest.mark.skipif(
        os.environ.get("DOCKER") != "true",
        reason="This test can only be run inside Docker"
    )
    def test_can_write_file_across_fs_boundary(self):
        # The temporary location used by the file manager and the directories
        # created for tests are on the same partition.  What if they're on
        # different partitions?
        manager = self.create_manager("/documents")
        jpg_data = pathlib.Path("tests/files/bridge.jpg").read_bytes()
        manager.write_bytes(file_id="1234", buffer=jpg_data)


class TestFileManager(FileManagerTestMixin):
    def create_manager(self, store_root):
        return FileManager(store_root)


class TestThumbnailManager(FileManagerTestMixin):
    def create_manager(self, store_root):
        return ThumbnailManager(store_root)

    def test_creates_thumbnail(self, store_root):
        manager = self.create_manager(store_root)
        resp = manager.create_thumbnail(
            file_id="1234",
            original_file=pathlib.Path("tests/files/bridge.jpg")
        )
        assert resp == pathlib.Path("1/1234.jpg")
        assert (manager.root / resp).exists()
