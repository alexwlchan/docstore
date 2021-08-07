import concurrent.futures
import os

from docstore.file_normalisation import normalised_filename_copy


def test_copies_a_file(tmpdir):
    src = tmpdir / "src.txt"
    dst = tmpdir / "dst.txt"

    src.write("Hello world")
    assert not dst.exists()

    normalised_filename_copy(src=src, dst=dst)

    assert dst.read() == "Hello world"


def test_creates_intermediate_directories(tmpdir):
    src = tmpdir / "src.txt"
    dst = tmpdir / "1" / "2" / "3" / "dst.txt"

    src.write("Hello world")
    assert not dst.exists()

    normalised_filename_copy(src=src, dst=dst)

    assert dst.read() == "Hello world"


def test_copies_multiple_files_to_the_same_dst(tmpdir):
    src1 = tmpdir / "src1.txt"
    src2 = tmpdir / "src2.txt"
    src3 = tmpdir / "src3.txt"

    dst = tmpdir / "dst.txt"

    src1.write("Hello world")
    src2.write("Bonjour le monde")
    src3.write("Hallo Welt")

    normalised_filename_copy(src=src1, dst=dst)
    normalised_filename_copy(src=src2, dst=dst)
    normalised_filename_copy(src=src3, dst=dst)

    assert len([f for f in os.listdir(tmpdir) if "dst" in f]) == 3

    dst_contents = {
        open(os.path.join(tmpdir, f)).read() for f in os.listdir(tmpdir) if "dst" in f
    }

    assert dst_contents == {"Hello world", "Bonjour le monde", "Hallo Welt"}


def test_copies_multiple_files_concurrently(tmpdir):
    src1 = tmpdir / "src1.txt"
    src2 = tmpdir / "src2.txt"
    src3 = tmpdir / "src3.txt"

    dst = tmpdir / "dst.txt"

    src1.write("Hello world")
    src2.write("Bonjour le monde")
    src3.write("Hallo Welt")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(normalised_filename_copy, src=s, dst=dst)
            for s in (src1, src2, src3)
        }
        concurrent.futures.wait(futures)

    assert len([f for f in os.listdir(tmpdir) if "dst" in f]) == 3

    dst_contents = {
        open(os.path.join(tmpdir, f)).read() for f in os.listdir(tmpdir) if "dst" in f
    }

    assert dst_contents == {"Hello world", "Bonjour le monde", "Hallo Welt"}
