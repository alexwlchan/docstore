from PIL import Image


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
    im = Image.open(path)

    if im.is_animated:
        result = []
        for frame in range(im.n_frames):
            im.seek(frame)
            result.extend(_get_colors_from_im(im))
        return result
    else:
        return _get_colors_from_im(im)
