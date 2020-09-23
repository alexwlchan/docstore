import os
import subprocess
import tempfile

from PIL import Image, UnidentifiedImageError


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
        return im.n_frames > 1


def create_thumbnail(path, *, max_size):
    """
    Creates a thumbnail of the file at ``path``.

    Returns the path to the new file.
    """
    out_dir = tempfile.mkdtemp()

    if _is_animated_gif(path):
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
    else:
        subprocess.check_call(
            ["qlmanage", "-t", path, "-s", f"{max_size}x{max_size}", "-o", out_dir],
            stdout=subprocess.DEVNULL,
        )
        return os.path.join(out_dir, os.listdir(out_dir)[0])
