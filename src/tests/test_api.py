# -*- encoding: utf-8

import hashlib
import io
import time

import pytest

import api as service
import index_helpers


@pytest.fixture()
def api(store, monkeypatch):
    def mock_get_jpeg_preview(*args, **kwargs):
        assert len(args) == 1
        assert args[0].endswith("1/100.pdf")
        assert kwargs == {"height": 400, "width": 400}

        new_path = args[0].replace(".pdf", ".jpg")
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        open(new_path, "wb").write(b"thumbnail")
        return new_path

    with monkeypatch.context() as m:
        m.setattr(
            index_helpers.preview_manager,
            "get_jpeg_preview",
            mock_get_jpeg_preview)
        return service.create_api(store)


def test_non_post_to_upload_is_405(api):
    resp = api.requests.get("/upload")
    assert resp.status_code == 405


def test_not_uploading_file_or_including_data_is_400(api):
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
    {"sha256_checksum": hashlib.sha256().hexdigest()},
])
def test_can_upload_without_all_parameters(api, data):
    resp = api.requests.post("/upload", files={"file": io.BytesIO()}, data=data)
    assert resp.status_code == 201


def test_incorrect_checksum_is_400(api):
    resp = api.requests.post(
        "/upload",
        files={"file": io.BytesIO()},
        data={"sha256_checksum": "123...abc"}
    )
    assert resp.status_code == 400


def test_stores_document_in_store(api, store):
    data = {
        "title": "Hello world",
        "tags": "foo bar baz",
        "filename": "foo.pdf",
        "sha256_checksum": hashlib.sha256().hexdigest(),
    }
    resp = api.requests.post("/upload", files={"file": io.BytesIO()}, data=data)
    assert resp.status_code == 201
    assert list(resp.json().keys()) == ["id"]

    docid = resp.json()["id"]
    stored_doc = store.documents[docid]
    assert stored_doc["title"] == data["title"]
    assert stored_doc["tags"] == data["tags"].split()
    assert stored_doc["filename"] == data["filename"]
    assert stored_doc["sha256_checksum"] == data["sha256_checksum"]


def test_extra_keys_are_kept_in_store(api, store):
    data = {
        "title": "Hello world",
        "tags": "foo bar baz",
        "filename": "foo.pdf",
        "sha256_checksum": hashlib.sha256().hexdigest(),
        "key1": "value1",
        "key2": "value2"
    }
    resp = api.requests.post("/upload", files={"file": io.BytesIO()}, data=data)
    assert resp.status_code == 201
    assert list(resp.json().keys()) == ["id"]

    docid = resp.json()["id"]
    stored_doc = store.documents[docid]
    assert stored_doc["user_data"] == {
        "key1": "value1",
        "key2": "value2",
    }


def test_calls_create_thumbnail(api, store, pdf_file):
    resp = api.requests.post("/upload", files={"file": pdf_file})
    assert resp.status_code == 201

    now = time.time()
    while time.time() - now < 5:
        docid = resp.json()["id"]
        stored_doc = store.documents[docid]
        if "thumbnail_path" in stored_doc.data:
            break

    assert "thumbnail_path" in stored_doc.data


def test_get_view_endpoint(api):
    resp = api.requests.get("/")
    assert resp.status_code == 200

    data = {
        "title": "Hello world"
    }
    api.requests.post("/upload", files={"file": io.BytesIO()}, data=data)

    resp = api.requests.get("/")
    assert resp.status_code == 200
    assert data["title"] in resp.text
