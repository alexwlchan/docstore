import os
import pathlib

import pytest


@pytest.fixture
def root(tmpdir):
    os.makedirs(str(tmpdir / "root"))
    return pathlib.Path(str(tmpdir / "root"))
