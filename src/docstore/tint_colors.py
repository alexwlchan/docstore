from PIL import Image


def get_colors_from(path):
    """
    Returns a list of the colors in the image at ``path``.
    """
    im = Image.open(path)

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
