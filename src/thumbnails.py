# -*- encoding: utf-8

import logging
import mimetypes
import os
import subprocess
import tempfile
import zipfile

from preview_generator.exception import UnsupportedMimeType
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
    with zipfile.ZipFile(open(path, "rb")) as epub:
        images = [
            f
            for f in epub.filelist
            if f.filename.endswith((".jpg", ".jpeg", ".png"))
        ]

        biggest_image = max(images, key=lambda f: f.file_size)
        return epub.extract(biggest_image, path=tempfile.mkdtemp())


def _get_imagemagick_preview(path):
    _, ext = os.path.splitext(path)
    _, out_path = tempfile.mkstemp(suffix=ext)
    if ext == ".gif":
        subprocess.check_call([
            "convert", path, "-coalesce", "-resize", "400x", "-deconstruct", out_path
        ])
    else:
        subprocess.check_call(["convert", path, "-thumbnail", "400x", out_path])
    return out_path


def _get_preview_manager_preview(path):
    pm_path = PREVIEW_MANAGER.get_jpeg_preview(path, height=1200, width=1200)
    return _get_imagemagick_preview(pm_path)



def create_thumbnail(path):
    _, ext = os.path.splitext(path)

    if ext == ".epub":
        epub_thumbnail_path = _get_epub_cover(path)
        thumbnail_path = _get_imagemagick_preview(epub_thumbnail_path)
        os.unlink(epub_thumbnail_path)
        return thumbnail_path

    elif mimetypes.guess_type(path)[0].startswith("image/"):
        return _get_imagemagick_preview(path)

    else:
        return _get_preview_manager_preview(path)
