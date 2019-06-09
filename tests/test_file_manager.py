# -*- encoding: utf-8

import pathlib

import pytest

from file_manager import FileManager


@pytest.fixture
def manager(tmpdir):
    return FileManager(root=pathlib.Path(tmpdir))


def test_shards_filenames(manager):
    resp = manager.write_bytes(file_id="1234", buffer=b"hello world")
    assert resp.parent == pathlib.Path("1")
    assert str(resp).startswith("1/1234")


def test_writes_bytes_to_disk(manager):
    resp = manager.write_bytes(file_id="1234", buffer=b"hello world")
    assert (manager.root / resp).read_bytes() == b"hello world"


def test_creates_intermediate_directories(tmpdir):
    root = pathlib.Path(tmpdir) / "1/2/3"
    manager = FileManager(root)

    resp = manager.write_bytes(file_id="1234", buffer=b"hello world")
    assert (manager.root / resp).read_bytes() == b"hello world"


@pytest.mark.parametrize("filename, expected_extension", [
    ("example.jpg", ".jpg"),
    ("document.pdf", ".pdf"),
    ("data.txt", ".txt"),
])
def test_uses_filename_extension_if_present(manager, filename, expected_extension):
    resp = manager.write_bytes(
        file_id="1234", buffer=b"hello world", original_filename=filename
    )
    assert resp.suffix == expected_extension


def test_detects_file_extension(manager):
    png_data = pathlib.Path("tests/files/cluster.png").read_bytes()
    resp = manager.write_bytes(file_id="1234", buffer=png_data)
    assert resp.suffix == ".png"


def test_no_extension_if_it_cannot_detect_one(manager):
    epub_data = pathlib.Path("tests/files/metamorphosis.epub").read_bytes()
    resp = manager.write_bytes(file_id="1234", buffer=epub_data)
    assert resp.suffix == ""


def test_uses_correct_jpeg_extension(manager):
    jpg_data = pathlib.Path("tests/files/bridge.jpg").read_bytes()
    resp = manager.write_bytes(file_id="1234", buffer=jpg_data)
    assert resp.suffix == ".jpg"
