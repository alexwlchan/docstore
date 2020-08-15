# -*- encoding: utf-8

import pathlib

from PIL import Image
import pytest

from thumbnails import create_thumbnail


@pytest.mark.parametrize(
    "filename, expected_ext",
    [
        ("bridge.jpg", ".jpg"),
        ("cluster.png", ".png"),
        ("metamorphosis.epub", ".jpg"),
        ("snakes.pdf", ".jpg"),
    ]
)
def test_create_thumbnail(filename, expected_ext):
    path = pathlib.Path("tests/files") / filename
    result = create_thumbnail(path)
    assert result.suffix == expected_ext
    assert result.exists()


@pytest.mark.parametrize("filename", ["helloworld.rb", "README.md"])
def test_errors_if_cannot_create_thumbnail(filename):
    with pytest.raises(ValueError, match="Unsupported MIME type"):
        create_thumbnail(pathlib.Path(f"tests/files/{filename}"))


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


def test_creates_qpdf_thumbnail():
    path = pathlib.Path("tests/files/qpdfconvert.pdf")
    create_thumbnail(path)


def test_can_substitute_helvetica_in_pdf():
    # This PDF uses the Helvetica font, but it isn't embedded.  Check that
    # when the PDF gets thumbnailed, it isn't just white pixels -- some
    # approximation of the text gets included.
    path = pathlib.Path("tests/files/helvetica_with_no_embedded_fonts.pdf")
    result = create_thumbnail(path)

    im = Image.open(result)
    assert im.getcolors() != [(226000, 255)]
