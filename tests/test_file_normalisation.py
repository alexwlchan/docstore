import concurrent.futures
import os
import pathlib

from docstore.file_normalisation import normalised_filename_copy


def test_copies_a_file(tmpdir: pathlib.Path) -> None:
    src = tmpdir / "src.txt"
    dst = tmpdir / "dst.txt"

    src.write_text("Hello world")
    assert not dst.exists()

    normalised_filename_copy(src=str(src), dst=str(dst))

    assert dst.read_text() == "Hello world"


def test_creates_intermediate_directories(tmpdir: pathlib.Path) -> None:
    src = tmpdir / "src.txt"
    dst = tmpdir / "1" / "2" / "3" / "dst.txt"

    src.write_text("Hello world")
    assert not dst.exists()

    normalised_filename_copy(src=str(src), dst=str(dst))

    assert dst.read_text() == "Hello world"


def test_copies_multiple_files_to_the_same_dst(tmpdir: pathlib.Path) -> None:
    src1 = tmpdir / "src1.txt"
    src2 = tmpdir / "src2.txt"
    src3 = tmpdir / "src3.txt"

    dst = tmpdir / "dst.txt"

    src1.write_text("Hello world")
    src2.write_text("Bonjour le monde")
    src3.write_text("Hallo Welt")

    normalised_filename_copy(src=str(src1), dst=str(dst))
    normalised_filename_copy(src=str(src2), dst=str(dst))
    normalised_filename_copy(src=str(src3), dst=str(dst))

    assert len([f for f in os.listdir(tmpdir) if "dst" in f]) == 3

    dst_contents = {
        open(os.path.join(tmpdir, f)).read() for f in os.listdir(tmpdir) if "dst" in f
    }

    assert dst_contents == {"Hello world", "Bonjour le monde", "Hallo Welt"}


def test_copies_multiple_files_concurrently(tmpdir: pathlib.Path) -> None:
    src1 = tmpdir / "src1.txt"
    src2 = tmpdir / "src2.txt"
    src3 = tmpdir / "src3.txt"

    dst = tmpdir / "dst.txt"

    src1.write_text("Hello world")
    src2.write_text("Bonjour le monde")
    src3.write_text("Hallo Welt")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(normalised_filename_copy, src=str(s), dst=str(dst))
            for s in (src1, src2, src3)
        }
        concurrent.futures.wait(futures)

    assert len([f for f in os.listdir(tmpdir) if "dst" in f]) == 3

    dst_contents = {
        open(os.path.join(tmpdir, f)).read() for f in os.listdir(tmpdir) if "dst" in f
    }

    assert dst_contents == {"Hello world", "Bonjour le monde", "Hallo Welt"}
