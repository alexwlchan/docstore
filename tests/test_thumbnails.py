# -*- encoding: utf-8

import pathlib

from PIL import Image
import pytest
from preview_generator.exception import UnsupportedMimeType

from thumbnails import create_thumbnail


@pytest.mark.parametrize(
    "filename, expected_ext",
    [
        ("bridge.jpg", ".jpg"),
        ("cluster.png", ".png"),
        ("metamorphosis.epub", ".jpg"),
        ("snakes.pdf", ".jpeg"),
    ]
)
def test_create_thumbnail(filename, expected_ext):
    path = pathlib.Path("tests/files") / filename
    result = create_thumbnail(path)
    assert result.suffix == expected_ext
    assert result.exists()


def test_errors_if_cannot_create_thumbnail():
    with pytest.raises(UnsupportedMimeType):
        create_thumbnail(pathlib.Path("tests/files/helloworld.rb"))


def test_creates_animated_gif_thumbnail():
    path = pathlib.Path("tests/files/movingsun.gif")
    result = create_thumbnail(path)

    assert result.suffix == ".gif"
    im = Image.open(result)
    assert im.format == "GIF"
    im.seek(1)  # throws an EOFError if not animated


def test_creates_mobi_thumbnail():
    path = pathlib.Path("tests/files/grundfragen.mobi")
    result = create_thumbnail(path)

    assert result.suffix == ".jpeg"
    im = Image.open(result)
    assert im.format == "JPEG"
    assert im.size == (400, 631)
