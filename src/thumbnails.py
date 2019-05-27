# -*- encoding: utf-8

import logging
import mimetypes
import pathlib
import subprocess
import tempfile
import zipfile

from preview_generator.manager import PreviewManager
from preview_generator.utils import LOGGER_NAME as PREVIEW_GENERATOR_LOGGER_NAME


def create_preview_manager():
    # When you create an instance of `PreviewManager`, you get warnings
    # about builders with missing dependencies (e.g. inkscape).  This is
    # mostly noise, so turn off all the logging from preview_manager while
    # we construct a new instance.

    class NoBuilderWarningFilter(logging.Filter):
        def filter(self, record):
            return False

    logger = logging.getLogger(PREVIEW_GENERATOR_LOGGER_NAME)
    f = NoBuilderWarningFilter()
    logger.addFilter(f)
    pm = PreviewManager(tempfile.mkdtemp())
    logger.removeFilter(f)

    return pm


PREVIEW_MANAGER = create_preview_manager()


def _get_epub_cover(path):
    # Based on https://github.com/marianosimone/epub-thumbnailer
    # An epub is a zipfile, so look inside it for a cover image.
    with zipfile.ZipFile(path.open("rb")) as epub:
        images = [
            f
            for f in epub.filelist
            if f.filename.endswith((".jpg", ".jpeg", ".png"))
        ]

        biggest_image = max(images, key=lambda f: f.file_size)
        return pathlib.Path(epub.extract(biggest_image, path=tempfile.mkdtemp()))


def _get_imagemagick_preview(path):
    assert isinstance(path, pathlib.Path)
    _, out_path = tempfile.mkstemp(suffix=path.suffix)
    if path.suffix == ".gif":
        subprocess.check_call([
            "convert", str(path), "-coalesce", "-resize", "400x", "-deconstruct", out_path
        ])
    else:
        subprocess.check_call(["convert", str(path), "-thumbnail", "400x", out_path])
    return pathlib.Path(out_path)


def _get_preview_manager_preview(path):

    # Somewhere inside preview_manager it's calling `mimetypes.guess_type()`,
    # which you can't use with Pathlib.Path.  There's a patch to fix that;
    # when it's released (probably Python 3.8),  you can drop the casts.
    # See:
    #   https://bugs.python.org/issue34926
    #   https://github.com/python/cpython/pull/9777
    #
    pm_path = PREVIEW_MANAGER.get_jpeg_preview(str(path), height=1200, width=1200)
    return _get_imagemagick_preview(pathlib.Path(pm_path))


def create_thumbnail(path):
    assert isinstance(path, pathlib.Path)
    if path.suffix == ".epub":
        epub_thumbnail_path = _get_epub_cover(path)
        thumbnail_path = _get_imagemagick_preview(epub_thumbnail_path)
        epub_thumbnail_path.unlink()
        return thumbnail_path

    # You can't pass a Pathlib.Path instance into mimetypes.guess_type yet.
    # There's a patch to fix that; when it's released (probably Python 3.8),
    # you can drop the `str`()`.  See:
    #   https://bugs.python.org/issue34926
    #   https://github.com/python/cpython/pull/9777
    #
    elif mimetypes.guess_type(str(path))[0].startswith("image/"):
        return _get_imagemagick_preview(path)

    else:
        return _get_preview_manager_preview(path)
