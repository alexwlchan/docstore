# -*- encoding: utf-8

import tempfile

from preview_generator.manager import PreviewManager


preview_manager = PreviewManager(tempfile.mkdtemp())


def create_jpeg_thumbnail(path):
    return preview_manager.get_jpeg_preview(path, height=400, width=400)
