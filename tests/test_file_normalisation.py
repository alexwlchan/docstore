import concurrent.futures
import os
import pathlib

from docstore.file_normalisation import normalised_filename_copy


def test_copies_a_file(tmp_path: pathlib.Path) -> None:
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"

    src.write_text("Hello world")
    assert not dst.exists()

    normalised_filename_copy(src=str(src), dst=str(dst))

    assert dst.read_text() == "Hello world"


def test_creates_intermediate_directories(tmp_path: pathlib.Path) -> None:
    src = tmp_path / "src.txt"
    dst = tmp_path / "1" / "2" / "3" / "dst.txt"

    src.write_text("Hello world")
    assert not dst.exists()

    normalised_filename_copy(src=str(src), dst=str(dst))

    assert dst.read_text() == "Hello world"


def test_copies_multiple_files_to_the_same_dst(tmp_path: pathlib.Path) -> None:
    src1 = tmp_path / "src1.txt"
    src2 = tmp_path / "src2.txt"
    src3 = tmp_path / "src3.txt"

    dst = tmp_path / "dst.txt"

    src1.write_text("Hello world")
    src2.write_text("Bonjour le monde")
    src3.write_text("Hallo Welt")

    normalised_filename_copy(src=str(src1), dst=str(dst))
    normalised_filename_copy(src=str(src2), dst=str(dst))
    normalised_filename_copy(src=str(src3), dst=str(dst))

    assert len([f for f in os.listdir(tmp_path) if "dst" in f]) == 3

    dst_contents = {
        open(os.path.join(tmp_path, f)).read()
        for f in os.listdir(tmp_path)
        if "dst" in f
    }

    assert dst_contents == {"Hello world", "Bonjour le monde", "Hallo Welt"}


def test_copies_multiple_files_concurrently(tmp_path: pathlib.Path) -> None:
    src1 = tmp_path / "src1.txt"
    src2 = tmp_path / "src2.txt"
    src3 = tmp_path / "src3.txt"

    dst = tmp_path / "dst.txt"

    src1.write_text("Hello world")
    src2.write_text("Bonjour le monde")
    src3.write_text("Hallo Welt")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(normalised_filename_copy, src=str(s), dst=str(dst))
            for s in (src1, src2, src3)
        }
        concurrent.futures.wait(futures)

    assert len([f for f in os.listdir(tmp_path) if "dst" in f]) == 3

    dst_contents = {
        open(os.path.join(tmp_path, f)).read()
        for f in os.listdir(tmp_path)
        if "dst" in f
    }

    assert dst_contents == {"Hello world", "Bonjour le monde", "Hallo Welt"}
