from PIL import Image
import pytest

from docstore.thumbnails import create_thumbnail


@pytest.mark.parametrize(
    "filename", ["Newtons_cradle.gif", "Rotating_earth_(large).gif"]
)
def test_creates_thumbnail_of_animated_gif(filename):
    path = create_thumbnail(f"tests/files/{filename}", max_size=400)
    assert path.endswith(".mp4")


def test_creates_thumbnail_of_single_frame_gif():
    path = create_thumbnail(
        "tests/files/Rotating_earth_(large)_singleframe.gif", max_size=400
    )
    assert path.endswith(".png")

    im = Image.open(path)
    assert im.size == (400, 400)


def test_creates_thumbnail_of_png():
    path = create_thumbnail("tests/files/cluster.png", max_size=250)
    assert path.endswith("/cluster.png.png")

    im = Image.open(path)
    assert im.size == (250, 162)


def test_creates_thumbnail_of_pdf():
    path = create_thumbnail("tests/files/snakes.pdf", max_size=350)
    assert path.endswith("/snakes.pdf.png")

    im = Image.open(path)
    assert im.size == (247, 350)
