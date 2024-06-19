import colorsys
import subprocess
import typing

import wcag_contrast_ratio as contrast


Color: typing.TypeAlias = tuple[int, int, int]


def choose_tint_color_from_dominant_colors(
    dominant_colors: list[Color], background_color: Color
) -> Color:
    """
    Given a set of dominant colors (say, from a k-means algorithm) and the
    background against which they'll be displayed, choose a tint color.

    Both ``dominant_colors`` and ``background_color`` should be tuples in [0,1].
    """
    # The minimum contrast ratio for text and background to meet WCAG AA
    # is 4.5:1, so discard any dominant colours with a lower contrast.
    sufficient_contrast_colors = [
        col for col in dominant_colors if contrast.rgb(col, background_color) >= 4.5
    ]

    # If none of the dominant colours meet WCAG AA with the background,
    # try again with black and white -- every colour in the RGB space
    # has a contrast ratio of 4.5:1 with at least one of these, so we'll
    # get a tint colour, even if it's not a good one.
    #
    # Note: you could modify the dominant colours until one of them
    # has sufficient contrast, but that's omitted here because it adds
    # a lot of complexity for a relatively unusual case.
    if not sufficient_contrast_colors:
        return choose_tint_color_from_dominant_colors(
            dominant_colors=dominant_colors + [(0, 0, 0), (1, 1, 1)],
            background_color=background_color,
        )

    # Of the colors with sufficient contrast, pick the one with the
    # highest saturation.  This is meant to optimise for colors that are
    # more colourful/interesting than simple greys and browns.
    hsv_candidates = {
        tuple(rgb_col): colorsys.rgb_to_hsv(*rgb_col)
        for rgb_col in sufficient_contrast_colors
    }

    return max(hsv_candidates, key=lambda rgb_col: hsv_candidates[rgb_col][2])


def from_hex(hs: str) -> Color:
    """
    Returns an RGB tuple from a hex string, e.g. #ff0102 -> (255, 1, 2)
    """
    return int(hs[1:3], 16), int(hs[3:5], 16), int(hs[5:7], 16)


def choose_tint_color_for_file(path: str) -> Color:
    """
    Returns the tint colour for a file.
    """
    background_color = (1, 1, 1)

    cmd = ["dominant_colours", "--no-palette", "--max-colours=12", path]

    dominant_colors = [
        from_hex(line) for line in subprocess.check_output(cmd).splitlines()
    ]

    colors = [(r / 255, g / 255, b / 255) for r, g, b in dominant_colors]

    return choose_tint_color_from_dominant_colors(
        dominant_colors=colors, background_color=background_color
    )


def choose_tint_color(*, thumbnail_path: str, file_path: str) -> Color:
    # In general, we use the thumbnail to choose the tint color.  The thumbnail
    # is what the tint color will usually appear next to.  However, thumbnails
    # for animated GIFs are MP4 videos rather than images, so we need to go to
    # the original image to get the tint color.
    if file_path.endswith((".jpg", ".jpeg", ".gif", ".png")):
        return choose_tint_color_for_file(file_path)
    else:
        return choose_tint_color_for_file(thumbnail_path)
