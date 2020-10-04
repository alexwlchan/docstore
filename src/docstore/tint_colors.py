import collections
import colorsys
import json
import math
import os

from PIL import Image, UnidentifiedImageError
from sklearn.cluster import KMeans
import wcag_contrast_ratio as contrast


def _get_colors_from_im(im):
    # Resizing means less pixels to handle, so the *k*-means clustering converges
    # faster.  Small details are lost, but the main details will be preserved.
    if im.size > (100, 100):
        resize_ratio = min([100 / im.width, 100 / im.height])

        new_width = int(im.width * resize_ratio)
        new_height = int(im.height * resize_ratio)

        im = im.resize((new_width, new_height))

    # Ensure the image is RGB for consistency.
    im = im.convert("RGB")

    return list(im.getdata())


def get_colors_from(path):
    """
    Returns a list of the colors in the image at ``path``.
    """
    im = Image.open(str(path))

    if getattr(im, "is_animated", False):
        result = []

        frame_count = im.n_frames

        # Don't get all the frames from an animated GIF; if it has hundreds of
        # frames this massively increases computation required for little gain.
        # Take a sample and work from that.
        for frame in range(0, frame_count, int(math.ceil(frame_count / 25))):
            im.seek(frame)
            result.extend(_get_colors_from_im(im))
        return result
    else:
        return _get_colors_from_im(im)


def choose_tint_color_from_dominant_colors(dominant_colors, background_color):
    """
    Given a set of dominant colors (say, from a k-means algorithm) and the
    background against which they'll be displayed, choose a tint color.

    Both ``dominant_colors`` and ``background_color`` should be tuples in [0,1].
    """
    # Clamp colours to the range 0.0 - 1.0; occasionally sklearn has spat out
    # numbers outside this range.
    dominant_colors = [
        (min(max(col[0], 0), 1), min(max(col[1], 0), 1), min(max(col[2], 0), 1))
        for col in dominant_colors
    ]

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


def choose_tint_color(*, paths, background_color):
    try:
        background_color = {"black": (0, 0, 0), "white": (1, 1, 1)}[background_color]
    except KeyError:  # pragma: no cover
        raise ValueError(f"Unrecognised background color: {background_color!r}")

    colors = []

    for p in paths:
        colors.extend(get_colors_from(p))

    if not colors:
        return ""

    # Normalise to [0, 1]
    colors = [(r / 255, g / 255, b / 255) for (r, g, b) in colors]

    pixel_tally = collections.Counter(colors)
    most_common, most_common_count = pixel_tally.most_common(1)[0]
    if (
        most_common_count >= len(colors) * 0.15
        and contrast.rgb(most_common, background_color) >= 4.5
    ):
        return most_common

    dominant_colors = KMeans(n_clusters=12).fit(colors).cluster_centers_

    return choose_tint_color_from_dominant_colors(
        dominant_colors=dominant_colors, background_color=background_color
    )


def get_tint_colors(root):
    try:
        return json.load(open(os.path.join(root, "tint_colors.json")))
    except FileNotFoundError:
        return {}


def store_tint_color(root, *, document):
    tint_colors = get_tint_colors(root)

    paths = []

    # In general, we use the thumbnail to choose the tint color.  The thumbnail
    # is what the tint color will usually appear next to.  However, thumbnails
    # for animated GIFs are MP4 videos rather than images, so we need to go to
    # the original image to get the tint color.
    for f in document.files:
        try:
            Image.open(os.path.join(root, f.thumbnail.path))
            paths.append(os.path.join(root, f.thumbnail.path))
        except UnidentifiedImageError:
            paths.append(os.path.join(root, f.path))

    tint_colors[document.id] = choose_tint_color(paths=paths, background_color="white")

    with open(os.path.join(root, "tint_colors.json"), "w") as outfile:
        outfile.write(json.dumps(tint_colors, indent=2, sort_keys=True))
