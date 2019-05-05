# -*- encoding: utf-8

import os

import pytest
from preview_generator.exception import UnsupportedMimeType

from thumbnails import create_thumbnail


@pytest.mark.parametrize(
    "filename",
    ["bridge.jpg", "cluster.png", "metamorphosis.epub", "snakes.pdf"]
)
def test_create_thumbnail(filename):
    path = os.path.join("tests", "files", filename)
    result = create_thumbnail(path)
    assert result.endswith(".jpg")
    assert os.path.exists(result)
    os.unlink(result)


def test_errors_if_cannot_create_thumbnail():
    with pytest.raises(UnsupportedMimeType):
        create_thumbnail(os.path.join("tests", "files", "helloworld.rb"))
