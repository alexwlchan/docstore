# -*- encoding: utf-8

import io

import pytest

from api import api


def test_non_post_to_upload_is_405():
    resp = api.requests.get("/upload")
    assert resp.status_code == 405


def test_not_uploading_file_is_400():
    resp = api.requests.post("/upload")
    assert resp.status_code == 400
    assert resp.json() == {
        "error": "Unexpected mimetype in content-type: ''"
    }


def test_not_uploading_file_is_400():
    resp = api.requests.post("/upload", data={"foo": "bar"})
    assert resp.status_code == 400
    assert resp.json() == {
        "error": "Unexpected mimetype in content-type: 'application/x-www-form-urlencoded'"
    }


def test_uploading_file_with_wrong_name_is_400():
    resp = api.requests.post("/upload", files={"data": io.BytesIO()})
    assert resp.status_code == 400
    assert resp.json() == {
        "error": "Unable to find multipart upload 'file'!"
    }
