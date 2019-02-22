# -*- encoding: utf-8

import hashlib
import io
import time

import bs4
import pytest

import api as service


@pytest.fixture()
def api(store):
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


def pdf_hash():
    h = hashlib.sha256()
    h.update(open("tests/snakes.pdf", "rb").read())
    return h.hexdigest()


@pytest.mark.parametrize('data', [
    {},
    {"title": "Hello world"},
    {"tags": ["foo"]},
    {"filename": "foo.pdf"},
    {"sha256_checksum": pdf_hash()},
])
def test_can_upload_without_all_parameters(api, data, pdf_file):
    resp = api.requests.post("/upload", files={"file": pdf_file}, data=data)
    assert resp.status_code == 201


def test_incorrect_checksum_is_400(api, pdf_file):
    resp = api.requests.post(
        "/upload",
        files={"file": pdf_file},
        data={"sha256_checksum": "123...abc"}
    )
    assert resp.status_code == 400


def test_stores_document_in_store(api, store, pdf_file):
    h = hashlib.sha256()
    h.update(open("tests/snakes.pdf", "rb").read())

    data = {
        "title": "Hello world",
        "tags": "foo bar baz",
        "filename": "foo.pdf",
        "sha256_checksum": h.hexdigest(),
    }
    resp = api.requests.post("/upload", files={"file": pdf_file}, data=data)
    assert resp.status_code == 201
    assert list(resp.json().keys()) == ["id"]

    docid = resp.json()["id"]
    stored_doc = store.documents[docid]
    assert stored_doc["title"] == data["title"]
    assert stored_doc["tags"] == data["tags"].split()
    assert stored_doc["filename"] == data["filename"]
    assert stored_doc["sha256_checksum"] == data["sha256_checksum"]


def test_extra_keys_are_kept_in_store(api, store, pdf_file):
    data = {
        "title": "Hello world",
        "tags": "foo bar baz",
        "filename": "foo.pdf",
        "key1": "value1",
        "key2": "value2"
    }
    resp = api.requests.post("/upload", files={"file": pdf_file}, data=data)
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
    while time.time() - now < 5:  # pragma: no cover
        docid = resp.json()["id"]
        stored_doc = store.documents[docid]
        if "thumbnail_identifier" in stored_doc.data:
            break

    assert "thumbnail_identifier" in stored_doc.data


def test_get_view_endpoint(api, pdf_file):
    resp = api.requests.get("/")
    assert resp.status_code == 200

    data = {
        "title": "Hello world"
    }
    api.requests.post("/upload", files={"file": pdf_file}, data=data)

    resp = api.requests.get("/")
    assert resp.status_code == 200
    assert data["title"] in resp.text


def test_can_view_file_and_thumbnail(api, pdf_file, file_identifier):
    api.requests.post("/upload", files={"file": pdf_file})
    time.sleep(2)

    resp = api.requests.get("/")
    assert resp.status_code == 200

    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    all_links = soup.find_all("a", attrs={"target": "_blank"})
    pdf_links = [
        link.attrs["href"]
        for link in all_links
        if link.attrs.get("href", "").endswith(".pdf")
    ]
    assert len(pdf_links) == 1
    pdf_href = pdf_links[0]

    thumbnails_td = soup.find_all("td", attrs={"class": "thumbnail"})
    assert len(thumbnails_td) == 1
    thumbnails_img = thumbnails_td[0].find_all("img")
    assert len(thumbnails_img) == 1
    img_src = thumbnails_img[0].attrs["src"]

    pdf_resp = api.requests.get(pdf_href, stream=True)
    assert pdf_resp.status_code == 200
    assert pdf_resp.raw.read() == open("tests/snakes.pdf", "rb").read()

    now = time.time()
    while time.time() - now < 3:  # pragma: no cover
        try:
            api.requests.get(img_src)
        except TypeError:
            pass
        else:
            break

    img_resp = api.requests.get(img_src)
    assert img_resp.status_code == 200


def test_can_lookup_document(api, pdf_file):
    data = {
        "title": "Hello world"
    }
    resp = api.requests.post("/upload", files={"file": pdf_file}, data=data)

    doc_id = resp.json()["id"]

    resp = api.requests.get(f"/documents/{doc_id}")
    assert resp.status_code == 200
    assert data["title"] == resp.json()["title"]


def test_lookup_missing_document_is_404(api):
    resp = api.requests.get("/documents/doesnotexist")
    assert resp.status_code == 404


def test_resolves_css(api):
    resp = api.requests.get("/")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    css_links = [
        link.attrs["href"]
        for link in soup.find_all("link", attrs={"rel": "stylesheet"})
    ]

    local_links = [link for link in css_links if not link.startswith("https://")]
    assert len(local_links) == 1
    css_link = local_links[0]

    assert css_link.endswith(".css")
    css_resp = api.requests.get(css_link)
    assert css_resp.status_code == 200
