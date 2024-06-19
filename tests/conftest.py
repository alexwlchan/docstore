import os
import pathlib

import pytest


@pytest.fixture
def root(tmpdir: pathlib.Path) -> pathlib.Path:
    os.makedirs(str(tmpdir / "root"))
    return pathlib.Path(str(tmpdir / "root"))
