# -*- encoding: utf-8

def safe_write(path, data):
    with open(path, "wb") as outfile:
        outfile.write(data)

    return path


from concurrent.futures import as_completed, ThreadPoolExecutor

from hypothesis import given
from hypothesis.strategies import binary


@given(binary())
def test_writes_to_given_filename_by_default(tmpdir, data):
    path = tmpdir / "greeting.txt"
    assert safe_write(path, data = data) == path

    assert path.exists()
    assert path.read_binary() == data


def test_writes_to_different_filenames_if_running_concurrently(tmpdir):
    path = tmpdir / "greeting.txt"

    thread_count = 10

    messages = [
        b"this is file %d" % i for i in range(thread_count)
    ]

    futures = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(thread_count):
            future = executor.submit(safe_write, path, messages[i])
            futures.append(future)

    filenames = set()
    for future in as_completed(futures):
        filenames.add(future.result())

    assert len(filenames) == thread_count

    written_messages = {
        f.read_binary() for f in filenames
    }

    assert written_messages == set(messages)
