import pytest

from docstore.thumbnails import create_thumbnail
from docstore.tint_colors import (
    choose_tint_color_from_dominant_colors,
    choose_tint_color,
)


def test_choose_tint_color():
    thumbnail_path = create_thumbnail("tests/files/Newtons_cradle.gif")

    tint_color = choose_tint_color(
        thumbnail_path=thumbnail_path, file_path="tests/files/Newtons_cradle.gif"
    )
    assert all(0.4 <= c <= 0.5 for c in tint_color), tint_color


@pytest.mark.parametrize(
    "dominant_color, background_color, expected_tint",
    [
        ((1, 1, 1), (1, 1, 1), (0, 0, 0)),
        ((0.9, 0.9, 0.9), (1, 1, 1), (0, 0, 0)),
        ((0, 0, 0), (0, 0, 0), (1, 1, 1)),
    ],
)
def test_selects_black_or_white_if_unsufficient_contrast(
    dominant_color, background_color, expected_tint
):
    assert (
        choose_tint_color_from_dominant_colors(
            dominant_colors=[dominant_color], background_color=background_color
        )
        == expected_tint
    )
