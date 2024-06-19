import pathlib

from PIL import Image
import pytest

from docstore.thumbnails import create_thumbnail, get_dimensions


@pytest.mark.parametrize(
    "filename", ["Newtons_cradle.gif", "Rotating_earth_(large).gif"]
)
def test_creates_thumbnail_of_animated_gif(filename: str) -> None:
    path = create_thumbnail(f"tests/files/{filename}", max_size=400)
    assert path.endswith(".mp4")


def test_creates_thumbnail_of_single_frame_gif() -> None:
    path = create_thumbnail(
        "tests/files/Rotating_earth_(large)_singleframe.gif", max_size=400
    )
    assert path.endswith(".png")

    im = Image.open(path)
    assert im.size == (400, 400)


def test_creates_thumbnail_of_png() -> None:
    path = create_thumbnail("tests/files/cluster.png", max_size=250)
    assert path.endswith("/cluster.png")

    im = Image.open(path)
    assert im.size == (250, 162)


def test_creates_thumbnail_of_pdf() -> None:
    path = create_thumbnail("tests/files/snakes.pdf", max_size=350)
    assert path.endswith("/snakes.pdf.png")

    im = Image.open(path)
    assert im.size == (247, 350)


def test_creates_thumbnail_if_no_quicklook_plugin_available(
    tmpdir: pathlib.Path,
) -> None:
    path = str(tmpdir / "sqlite.db")

    with open(path, "wb") as outfile:
        outfile.write(b"SQLite format 3\x00")

    path = create_thumbnail(path)


def test_gets_dimensions_of_an_image() -> None:
    dimensions = get_dimensions("tests/files/cluster.png")
    assert dimensions.width == 500
    assert dimensions.height == 325


def test_gets_dimensions_of_a_video() -> None:
    thumbnail_path = create_thumbnail("tests/files/Newtons_cradle.gif")

    dimensions = get_dimensions(thumbnail_path)
    assert dimensions.width == 400
    assert dimensions.height == 300
