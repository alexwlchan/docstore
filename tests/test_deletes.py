# -*- encoding: utf-8

import io
import json


def test_delete_non_existent_document_is_404(app):
    resp = app.delete("/documents/doesnotexist")
    assert resp.status_code == 404


def test_can_delete_a_document(app, store_root):
    # Check we can upload and retrieve the document successfully
    upload_resp = app.post("/upload", data={
        "title": "hello world",
        "file": (io.BytesIO(b"hello world"), "greeting.txt")
    })
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json["id"]

    get_resp = app.get(f"/documents/{doc_id}")
    doc_data = get_resp.json

    # Now delete the document
    delete_resp = app.delete(f"/documents/{doc_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json == {"deleted": "ok"}

    # Check we can no longer retrieve the document
    get_resp = app.get(f"/documents/{doc_id}")
    assert get_resp.status_code == 404

    # Check the data has been soft-copied outside the main database
    json_path = store_root / "deleted" / f"{doc_id}.json"
    assert json.load(json_path.open()) == {
        key: value
        for key, value in doc_data.items()
        if key != "thumbnail_identifier"
    }

    file_path = store_root / "deleted" / doc_data["file_identifier"]
    assert file_path.read_bytes() == b"hello world"

    # Check the original file has been deleted
    assert not (store_root / "files" / doc_data["file_identifier"]).exists()

    file_get_resp = app.get(f"/files/{doc_data['file_identifier']}")
    assert file_get_resp.status_code == 404


def test_deleting_one_doc_does_not_affect_others(app):
    upload_resp = app.post("/upload", data={
        "title": "file to delete",
        "file": (io.BytesIO(b"hello world"), "greeting.txt")
    })
    assert upload_resp.status_code == 201
    to_delete_doc_id = upload_resp.json["id"]

    upload_resp = app.post("/upload", data={
        "title": "file to keep",
        "file": (io.BytesIO(b"hello world"), "greeting.txt")
    })
    assert upload_resp.status_code == 201
    to_keep_doc_id = upload_resp.json["id"]

    delete_resp = app.delete(f"/documents/{to_delete_doc_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json == {"deleted": "ok"}

    get_resp = app.get(f"/documents/{to_keep_doc_id}")
    assert get_resp.status_code == 200


def test_can_delete_png_file(app, store_root, png_file):
    # Check we can upload and retrieve the document successfully
    upload_resp = app.post("/upload", data={
        "title": "hello world",
        "file": (png_file, "example.png")
    })
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json["id"]

    get_resp = app.get(f"/documents/{doc_id}")
    doc_data = get_resp.json

    # Now delete the document
    delete_resp = app.delete(f"/documents/{doc_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json == {"deleted": "ok"}

    # Check the thumbnail has been deleted
    assert not (store_root / "thumbnails" / doc_data["thumbnail_identifier"]).exists()

    thumbnail_get_resp = app.get(f"/thumbnails/{doc_data['thumbnail_identifier']}")
    assert thumbnail_get_resp.status_code == 404
