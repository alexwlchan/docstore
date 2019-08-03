# -*- encoding: utf-8

import io
import json
import hashlib
import time

import bs4
import hyperlink
import pytest

import api as service


def sha256(f):
    h = hashlib.sha256()

    while True:
        next_buffer = f.read(65536)
        if not next_buffer:
            break
        h.update(next_buffer)

    return h.hexdigest()


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


with open("tests/files/snakes.pdf", "rb") as f:
    snake_sha256 = sha256(f)


@pytest.mark.parametrize('data', [
    {},
    {"title": "Hello world"},
    {"tags": ["foo"]},
    {"filename": "foo.pdf"},
])
def test_can_upload_without_all_parameters(api, data, pdf_file):
    resp = api.requests.post("/upload", files={"file": pdf_file}, data=data)
    assert resp.status_code == 201


def test_stores_document_in_store(api, tagged_store, pdf_file, pdf_path):
    hex_hash = sha256(pdf_path.open("rb"))

    data = {
        "title": "Hello world",
        "tags": "foo bar baz",
        "filename": "foo.pdf",
    }
    resp = api.requests.post("/upload", files={"file": pdf_file}, data=data)
    assert resp.status_code == 201
    assert list(resp.json().keys()) == ["id"]

    docid = resp.json()["id"]
    stored_doc = tagged_store.objects[docid]
    assert stored_doc["title"] == data["title"]
    assert stored_doc["tags"] == data["tags"].split()
    assert stored_doc["filename"] == data["filename"]
    assert "checksum" in stored_doc


def test_extra_keys_are_kept_in_store(api, tagged_store, pdf_file):
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
    stored_doc = tagged_store.objects[docid]
    assert stored_doc["user_data"] == {
        "key1": "value1",
        "key2": "value2",
    }


def test_calls_create_thumbnail(api, tagged_store, pdf_file):
    resp = api.requests.post("/upload", files={"file": pdf_file})
    assert resp.status_code == 201
    doc_id = resp.json()["id"]

    now = time.time()
    while time.time() - now < 10:  # pragma: no cover
        stored_doc = tagged_store.objects[doc_id]
        if "thumbnail_identifier" in stored_doc:
            break

    assert "thumbnail_identifier" in stored_doc


def test_recreates_thumbnail(api, tagged_store, store_root, pdf_file):
    resp = api.requests.post("/upload", files={"file": pdf_file})
    assert resp.status_code == 201
    doc_id = resp.json()["id"]

    now = time.time()
    while time.time() - now < 10:  # pragma: no cover
        stored_doc = tagged_store.objects[doc_id]
        if "thumbnail_identifier" in stored_doc:
            break

    thumb_path = store_root / "thumbnails" / stored_doc["thumbnail_identifier"]
    assert thumb_path.exists()
    original_mtime = thumb_path.stat().st_mtime

    resp = api.requests.post("/api/v1/recreate_thumbnails")
    assert resp.status_code == 202
    assert resp.json() == {"ok": "true"}

    now = time.time()
    while time.time() - now < 10:  # pragma: no cover
        try:
            if thumb_path.stat().st_mtime != original_mtime:
                break
        except FileNotFoundError:
            pass

    assert thumb_path.stat().st_mtime > original_mtime


def test_can_only_post_to_recreate_thumbnail(api):
    resp = api.requests.get("/api/v1/recreate_thumbnails")
    assert resp.status_code == 405


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


def test_can_view_file_and_thumbnail(api, pdf_file, pdf_path, file_identifier):
    api.requests.post("/upload", files={"file": pdf_file})
    time.sleep(1)

    resp = api.requests.get("/")
    assert resp.status_code == 200
    assert resp.text != "null"

    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    all_links = soup.find_all("a", attrs={"target": "_blank"})
    pdf_links = list(set(
        link.attrs["href"]
        for link in all_links
        if link.attrs.get("href", "").endswith(".pdf")
    ))
    assert len(pdf_links) == 1
    pdf_href = pdf_links[0]

    thumbnails_div = soup.find_all("div", attrs={"class": "document__image"})
    assert len(thumbnails_div) == 1
    thumbnails_img = thumbnails_div[0].find_all("img")
    assert len(thumbnails_img) == 1
    img_src = thumbnails_img[0].attrs["src"]

    pdf_resp = api.requests.get(pdf_href, stream=True)
    assert pdf_resp.status_code == 200
    assert pdf_resp.raw.read() == open(pdf_path, "rb").read()

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


def test_can_view_existing_file_and_thumbnail(
    api, tagged_store, store_root, pdf_file, pdf_path, file_identifier
):
    api.requests.post("/upload", files={"file": pdf_file})

    # Wait for the document to index, then create a fresh API at the same root
    time.sleep(1)
    new_api = service.create_api(tagged_store, root=store_root)

    resp = new_api.requests.get("/")
    assert resp.status_code == 200
    assert resp.text != "null"

    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    all_links = soup.find_all("a", attrs={"target": "_blank"})
    pdf_links = list(set(
        link.attrs["href"]
        for link in all_links
        if link.attrs.get("href", "").endswith(".pdf")
    ))
    assert len(pdf_links) == 1
    pdf_href = pdf_links[0]

    thumbnails_div = soup.find_all("div", attrs={"class": "document__image"})
    assert len(thumbnails_div) == 1
    thumbnails_img = thumbnails_div[0].find_all("img")
    assert len(thumbnails_img) == 1
    img_src = thumbnails_img[0].attrs["src"]

    pdf_resp = new_api.requests.get(pdf_href, stream=True)
    assert pdf_resp.status_code == 200
    assert pdf_resp.raw.read() == open(pdf_path, "rb").read()

    now = time.time()
    while time.time() - now < 3:  # pragma: no cover
        try:
            new_api.requests.get(img_src)
        except TypeError:
            pass
        else:
            break

    img_resp = new_api.requests.get(img_src)
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


@pytest.mark.parametrize("filename,expected_header", [
    ("example.pdf", "filename*=utf-8''example.pdf"),
])
def test_sets_content_disposition_header(api, pdf_file, filename, expected_header):
    resp = api.requests.post(
        "/upload",
        files={"file": pdf_file},
        data={"filename": filename}
    )

    doc_id = resp.json()["id"]

    resp = api.requests.get(f"/documents/{doc_id}")

    file_identifier = resp.json()["file_identifier"]
    resp = api.requests.get(f"/files/{file_identifier}")
    assert resp.headers["Content-Disposition"] == expected_header


def test_does_not_set_content_disposition_if_no_filename(api, pdf_file):
    resp = api.requests.post("/upload", files={"file": pdf_file})

    doc_id = resp.json()["id"]
    resp = api.requests.get(f"/files/{doc_id[0]}/{doc_id}.pdf")
    assert "Content-Disposition" not in resp.headers


class TestBrowser:
    """Tests for the in-browser functionality"""

    @staticmethod
    def upload(api, file_contents, data=None, referer=None):
        if data is None:
            data = {}
        referer = referer or "http://localhost:8072/"
        return api.requests.post(
            "/upload",
            files={"file": ("mydocument.pdf", file_contents, "application/pdf")},
            data=data,
            headers={"referer": referer}
        )

    def test_returns_302_redirect_to_original_page(self, api, pdf_file):
        original_page = "https://example.org/docstore/"
        resp = self.upload(api=api, file_contents=pdf_file, referer=original_page)

        assert resp.status_code == 302
        assert resp.headers["Location"].startswith(original_page)

    def test_includes_document_in_store(self, api, tagged_store, pdf_file):
        resp = self.upload(api=api, file_contents=pdf_file)

        location = hyperlink.URL.from_text(resp.headers["Location"])
        message = json.loads(dict(location.query)["_message"])

        docid = message["id"]
        stored_doc = tagged_store.objects[docid]
        assert stored_doc["filename"] == "mydocument.pdf"

    @pytest.mark.parametrize("view_option", ["table", "grid"])
    def test_includes_source_url_in_page(self, api, view_option, pdf_file):
        self.upload(
            api=api,
            file_contents=pdf_file,
            data={"source_url": "https://example.org/document.pdf"}
        )

        resp = api.requests.get("/", params={"view": view_option})
        assert '<a href="https://example.org/document.pdf">example.org</a>' in resp.text


class TestPrepareData:

    def test_deletes_empty_user_data_values(self):
        user_data = {
            "file": b"hello world",
            "source_url": b"https://example.org/",
            "external_identifier": b"",
        }

        prepared_data = service.prepare_form_data(user_data)
        assert prepared_data["user_data"] == {
            "source_url": "https://example.org/",
        }

    def test_deletes_empty_user_data(self):
        user_data = {
            "file": b"hello world",
            "external_identifier": b"",
        }

        prepared_data = service.prepare_form_data(user_data)
        assert "user_data" not in prepared_data

    def test_omits_user_data_if_no_extra_values(self):
        user_data = {"file": b"hello world"}

        prepared_data = service.prepare_form_data(user_data)
        assert "user_data" not in prepared_data

    def test_moves_sha256_checksum_to_user_data(self):
        user_data = {
            "file": b"hello world",
            "sha256_checksum": b"123456"
        }

        prepared_data = service.prepare_form_data(user_data)
        assert prepared_data["user_data"] == {
            "sha256_checksum": "123456"
        }
