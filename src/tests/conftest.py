# -*- encoding: utf-8

import shutil
import tempfile

import pytest

import api as service
from tagged_store import TaggedDocumentStore


@pytest.fixture
def store():
    root = tempfile.mkdtemp()
    yield TaggedDocumentStore(root=root)
    shutil.rmtree(root)


@pytest.fixture()
def api(store):
    service.api.store = store
    return service.api
