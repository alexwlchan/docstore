#!/usr/bin/env python
# -*- encoding: utf-8

import os
import shutil
import sys
import tempfile

from preview_generator.manager import PreviewManager

preview_manager = PreviewManager(tempfile.mkdtemp())

pdf_path = sys.argv[1]

thumbnail = preview_manager.get_jpeg_preview(
    pdf_path,
    height=1024,
    width=526
)

assert os.path.basename(thumbnail) != os.path.basename(pdf_path)
shutil.move(thumbnail, os.path.basename(thumbnail))
print(os.path.basename(thumbnail))
