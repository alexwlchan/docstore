# -*- encoding: utf-8

import io

import pytest


def test_non_post_to_upload_is_405(api):
    resp = api.requests.get("/upload")
    assert resp.status_code == 405


def test_not_uploading_file_is_400(api):
    resp = api.requests.post("/upload")
    assert resp.status_code == 400
    assert resp.json() == {
        "error": "Unexpected mimetype in content-type: ''"
    }


def test_not_uploading_file_is_400(api):
    resp = api.requests.post("/upload", data={"foo": "bar"})
    assert resp.status_code == 400
    assert resp.json() == {
        "error": "Unexpected mimetype in content-type: 'application/x-www-form-urlencoded'"
    }


def test_uploading_file_with_wrong_name_is_400(api):
    resp = api.requests.post("/upload", files={"data": io.BytesIO()})
    assert resp.status_code == 400
    assert resp.json() == {
        "error": "Unable to find multipart upload 'file'!"
    }


@pytest.mark.parametrize('data', [
    {},
    {"title": "Hello world"},
    {"tags": ["foo"]},
    {"filename": "foo.pdf"},
    {"sha256_checksum": "abc123"},
])
def test_can_upload_without_all_parameters(api, data):
    resp = api.requests.post("/upload", files={"file": io.BytesIO()}, data=data)
    assert resp.status_code == 200
