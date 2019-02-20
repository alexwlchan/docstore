# -*- encoding: utf-8

import pytest

from api import api


def test_non_post_to_upload_is_405():
    resp = api.requests.get("/upload")
    print(resp.text)
    assert resp.status_code == 405
