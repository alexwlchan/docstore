# -*- encoding: utf-8

from concurrent.futures import as_completed, ThreadPoolExecutor

from file_writer import safe_write


def test_writes_to_given_filename_by_default(tmpdir):
    path = pathlib.Path(tmpdir / "greeting.txt")
    assert safe_write(path, data = b"hello world") == path

    assert path.exists()
    assert path.read_bytes() == b"hello world"


def test_writes_to_different_filenames_if_running_concurrently(tmpdir):
    path = tmpdir / "greeting.txt"

    thread_count = 10

    messages = [
        b"this is file %d" % i for i in range(thread_count)
    ]

    futures = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(thread_count):
            future = executor.submit(safe_write, pathlib.Path(path), messages[i])
            futures.append(future)

    filenames = set()
    for future in as_completed(futures):
        filenames.add(future.result())

    assert len(filenames) == thread_count

    written_messages = {
        f.read_bytes() for f in filenames
    }

    assert written_messages == set(messages)
