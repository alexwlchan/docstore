# -*- encoding: utf-8

import logging
import mimetypes
import pathlib
import subprocess
import tempfile

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
    # Calling https://github.com/marianosimone/epub-thumbnailer
    # This gets installed into /tools, and I shell out to it with subprocess
    # so docstore doesn't get roped into using GPLv2.
    working_dir = pathlib.Path(tempfile.mkdtemp())

    out_file = working_dir / "cover.jpg"

    subprocess.check_call(
        [
            "python3", "/tools/epub-thumbnailer/src/epub-thumbnailer.py",

            # In file, out file, size (not used)
            path.resolve(), out_file, "1000"
        ]
    )

    return out_file


def _get_mobi_cover(path):
    # Calling https://github.com/alexwlchan/get-mobi-cover-image
    # This gets installed into /tools, and I shell out to it with subprocess
    # so docstore doesn't get roped into using GPLv2.
    working_dir = pathlib.Path(tempfile.mkdtemp())

    result = subprocess.check_output(
        ["python3", "/tools/get-mobi-cover-image/get_mobi_cover.py", path.resolve()],
        cwd=working_dir
    ).decode("utf-8").strip()

    return working_dir / result


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


def _get_pdf_preview(path):
    # https://alexwlchan.net/2019/07/creating-preview-thumbnails-of-pdf-documents/
    assert isinstance(path, pathlib.Path)
    _, out_path = tempfile.mkstemp()
    subprocess.check_call([
        "pdftocairo", str(path), "-jpeg", "-singlefile", "-scale-to-x", "1200", "-scale-to-y", "1", out_path
    ])
    jpg_path = pathlib.Path(out_path + ".jpg")
    assert jpg_path.exists()
    return jpg_path


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

    elif path.suffix == ".mobi":
        mobi_thumbnail_path = _get_mobi_cover(path)
        thumbnail_path = _get_imagemagick_preview(mobi_thumbnail_path)
        mobi_thumbnail_path.unlink()
        return thumbnail_path

    elif path.suffix == ".pdf":
        pdf_thumbnail_path = _get_pdf_preview(path)
        thumbnail_path = _get_imagemagick_preview(pdf_thumbnail_path)
        pdf_thumbnail_path.unlink()
        return thumbnail_path

    # You can't pass a Pathlib.Path instance into mimetypes.guess_type yet.
    # There's a patch to fix that; when it's released (probably Python 3.8),
    # you can drop the `str`()`.  See:
    #   https://bugs.python.org/issue34926
    #   https://github.com/python/cpython/pull/9777
    #
    guessed_type = mimetypes.guess_type(str(path))[0]

    if guessed_type is not None and guessed_type.startswith("image/"):
        return _get_imagemagick_preview(path)
    else:
        raise ValueError(f"Unsupported MIME type: {guessed_type}")
