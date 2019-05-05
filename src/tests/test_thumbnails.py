# -*- encoding: utf-8

import os

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
    path = os.path.join("tests", "files", filename)
    result = create_thumbnail(path)
    assert result.endswith(expected_ext)
    assert os.path.exists(result)


def test_errors_if_cannot_create_thumbnail():
    with pytest.raises(UnsupportedMimeType):
        create_thumbnail(os.path.join("tests", "files", "helloworld.rb"))


def test_creates_animated_gif_thumbnail():
    path = os.path.join("tests", "files", "movingsun.gif")
    result = create_thumbnail(path)

    assert result.endswith(".gif")
    im = Image.open(result)
    assert im.format == "GIF"
    im.seek(1)  # throws an EOFError if not animated
