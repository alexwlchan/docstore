# -*- encoding: utf-8

def safe_write(path, data):
    with open(path, "wb") as outfile:
        outfile.write(data)

    return path


from hypothesis import given
from hypothesis.strategies import binary


@given(binary())
def test_writes_to_given_filename_by_default(tmpdir, data):
    path = tmpdir / "greeting.txt"
    assert safe_write(path, data = data) == path

    assert path.exists()
    assert path.read_binary() == data
