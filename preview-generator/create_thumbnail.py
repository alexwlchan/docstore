#!/usr/bin/env python
# -*- encoding: utf-8

import os
import shutil
import sys
import tempfile

from preview_generator.manager import PreviewManager

preview_manager = PreviewManager(tempfile.mkdtemp())

pdf_path = sys.argv[1]
thumbnail_path = sys.argv[2]

thumbnail = preview_manager.get_jpeg_preview(
    pdf_path,
    height=400,
    width=400
)

assert pdf_path != thumbnail_path
shutil.move(thumbnail, thumbnail_path)
print(thumbnail_path)
