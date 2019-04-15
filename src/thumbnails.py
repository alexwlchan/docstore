# -*- encoding: utf-8

import os
import tempfile
import zipfile

from preview_generator.exception import UnsupportedMimeType
from preview_generator.manager import PreviewManager


preview_manager = PreviewManager(tempfile.mkdtemp())


def _get_epub_cover(path):
    # An epub is a zipfile, so look inside it for a cover image.
    with zipfile.ZipFile(open(path, "rb")) as epub:
        images = [
            f
            for f in epub.filelist
            if f.filename.endswith((".jpg", ".jpeg", ".png"))
        ]

        biggest_image = max(images, key=lambda f: f.file_size)
        return epub.extract(biggest_image, path=tempfile.mkdtemp())


def create_jpeg_thumbnail(path):
    try:
        return preview_manager.get_jpeg_preview(path, height=400, width=400)
    except UnsupportedMimeType as err:
        if err.args == ("Unsupported mimetype: application/epub+zip",):
            epub_thumbnail_path = _get_epub_cover(path)
            thumbnail_path = preview_manager.get_jpeg_preview(epub_thumbnail_path)
            os.unlink(epub_thumbnail_path)
            return thumbnail_path
        raise
