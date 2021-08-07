import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, UnidentifiedImageError

from docstore.models import Dimensions


def _is_animated_gif(path):
    """
    Returns True if the file at ``path`` is an animated GIF.
    """
    try:
        im = Image.open(path)
    except UnidentifiedImageError:
        # Not an image
        return False
    else:
        return getattr(im, "is_animated", False)


def _create_gif_thumbnail_from_ffmpeg(*, path, max_size, out_dir):
    im = Image.open(path)

    if im.width > im.height and im.width >= max_size:
        width, height = (max_size, int(im.height * max_size / im.width))
    else:
        width, height = (int(im.width * max_size / im.height), max_size)

    # The yuv420p encoder requires even values
    width, height = (int(width / 2) * 2, int(height / 2) * 2)

    out_path = os.path.join(out_dir, os.path.basename(path) + ".mp4")

    subprocess.check_call(
        [
            "ffmpeg",
            "-i",
            path,
            "-movflags",
            "faststart",
            "-pix_fmt",
            "yuv420p",
            "-vf",
            f"scale={width}:{height}",
            out_path,
        ],
        stdout=subprocess.DEVNULL,
    )

    return out_path


def _create_thumbnail_from_quick_look(*, path, max_size, out_dir):
    try:
        subprocess.check_call(
            ["qlmanage", "-t", path, "-s", f"{max_size}x{max_size}", "-o", out_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
    except subprocess.TimeoutExpired:
        # It's possible for somethign to go wrong with the Quick Look
        # process where it just hangs and doesn't create a thumbnail.
        # If so, just continue without creating the thumbnail.
        pass

    try:
        result = os.path.join(out_dir, os.listdir(out_dir)[0])
    except IndexError:
        print(f"Quick Look could not create a thumbnail for {path}", file=sys.stderr)
        result = os.path.join(out_dir, "generic_document.png")
        shutil.copyfile(
            src=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "static/generic_document.png",
            ),
            dst=result,
        )

    if result.endswith(".png.png"):
        os.rename(result, result.replace(".png.png", ".png"))
        result = result.replace(".png.png", ".png")

    return result


def create_thumbnail(path, *, max_size=400):
    """
    Creates a thumbnail of the file at ``path``.

    Returns the path to the new file.
    """
    kwargs = {"path": path, "max_size": max_size, "out_dir": tempfile.mkdtemp()}

    if _is_animated_gif(path):
        return _create_gif_thumbnail_from_ffmpeg(**kwargs)
    else:
        return _create_thumbnail_from_quick_look(**kwargs)


def get_dimensions(path):
    """
    Returns the (width, height) of a given path.
    """
    if path.endswith(".png"):  # image thumbnail
        im = Image.open(path)
        return Dimensions(width=im.width, height=im.height)

    elif path.endswith(".mp4"):  # video thumbnail
        # See https://stackoverflow.com/a/29585066/1558022
        output = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=p=0:s=x",
                os.path.abspath(path),
            ]
        )
        width, height = output.strip().split(b"x")
        return Dimensions(width=int(width), height=int(height))

    else:  # pragma: no cover
        raise ValueError(f"Unrecognised thumbnail type: {path}")
