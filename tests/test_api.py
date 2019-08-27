# -*- encoding: utf-8

import io
import json
import multiprocessing
import time

import bs4
import hyperlink
import pytest

import api as service
from index_helpers import index_new_document


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


@pytest.mark.parametrize("data", [
    {},
    {"title": "Hello world"},
    {"tags": ["cluster"]},
    {"filename": "cluster.png"},
])
def test_can_upload_without_all_parameters(api, data, png_file):
    resp = api.requests.post("/upload", files={"file": png_file}, data=data)
    assert resp.status_code == 201


def test_stores_document_in_store(api, tagged_store, png_file, png_path):
    data = {
        "title": "Hello world",
        "tags": "cluster elasticsearch blue",
        "filename": "cluster.png",
    }
    resp = api.requests.post("/upload", files={"file": png_file}, data=data)
    assert resp.status_code == 201
    assert list(resp.json().keys()) == ["id"]

    docid = resp.json()["id"]
    stored_doc = tagged_store.objects[docid]
    assert stored_doc["title"] == data["title"]
    assert stored_doc["tags"] == data["tags"].split()
    assert stored_doc["filename"] == data["filename"]
    assert "checksum" in stored_doc


def test_extra_keys_are_kept_in_store(api, tagged_store, png_file):
    data = {
        "key1": "value1",
        "key2": "value2"
    }
    resp = api.requests.post("/upload", files={"file": png_file}, data=data)
    assert resp.status_code == 201
    assert list(resp.json().keys()) == ["id"]

    docid = resp.json()["id"]
    stored_doc = tagged_store.objects[docid]
    assert stored_doc["user_data"] == data


def test_calls_create_thumbnail(api, tagged_store, png_file):
    resp = api.requests.post("/upload", files={"file": png_file})
    assert resp.status_code == 201
    doc_id = resp.json()["id"]

    now = time.time()
    while time.time() - now < 10:  # pragma: no cover
        stored_doc = tagged_store.objects[doc_id]
        if "thumbnail_identifier" in stored_doc:
            break

    assert "thumbnail_identifier" in stored_doc


def test_get_view_endpoint(api, png_file):
    data = {
        "title": "Hello world"
    }
    api.requests.post("/upload", files={"file": png_file}, data=data)

    resp = api.requests.get("/")
    assert resp.status_code == 200
    assert data["title"] in resp.text


def test_can_view_file_and_thumbnail(api, png_file, png_path):
    api.requests.post("/upload", files={"file": png_file})

    resp = api.requests.get("/")
    assert resp.status_code == 200
    assert resp.text != "null"

    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    all_links = soup.find_all("a", attrs={"target": "_blank"})
    png_links = list(set(
        link.attrs["href"]
        for link in all_links
        if link.attrs.get("href", "").endswith(".png")
    ))
    assert len(png_links) == 1
    png_href = png_links[0]

    png_resp = api.requests.get(png_href, stream=True)
    assert png_resp.status_code == 200
    assert png_resp.raw.read() == open(png_path, "rb").read()

    thumbnails_div = soup.find_all("div", attrs={"class": "document__image"})
    assert len(thumbnails_div) == 1
    thumbnails_img = thumbnails_div[0].find_all("img")
    assert len(thumbnails_img) == 1
    thumb_src = thumbnails_img[0].attrs["src"]

    thumb_resp = api.requests.get(thumb_src)
    assert thumb_resp.status_code == 200


def test_can_view_existing_file_and_thumbnail(
<<<<<<< HEAD
    api, tagged_store, store_root, png_file, png_path
=======
    api, config, tagged_store, png_file, png_path
>>>>>>> Use the refactored CLI in the tests
):
    resp = api.requests.post("/upload", files={"file": png_file})
    doc_id = resp.json()["id"]

    # Wait until a thumbnail has been created before creating the new API.
    now = time.time()
    while time.time() - now < 3:  # pragma: no cover
        stored_doc = tagged_store.objects[doc_id]
        if "thumbnail_identifier" in stored_doc:
            break

    new_api = service.create_api(tagged_store, config=config)

    resp = new_api.requests.get("/")
    assert resp.status_code == 200
    assert resp.text != "null"

    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    all_links = soup.find_all("a", attrs={"target": "_blank"})
    png_links = list(set(
        link.attrs["href"]
        for link in all_links
        if link.attrs.get("href", "").endswith(".png")
    ))
    assert len(png_links) == 1
    png_href = png_links[0]

    png_resp = new_api.requests.get(png_href, stream=True)
    assert png_resp.status_code == 200
    assert png_resp.raw.read() == open(png_path, "rb").read()

    thumbnails_div = soup.find_all("div", attrs={"class": "document__image"})
    assert len(thumbnails_div) == 1
    thumbnails_img = thumbnails_div[0].find_all("img")
    assert len(thumbnails_img) == 1
    thumb_src = thumbnails_img[0].attrs["src"]

    thumb_resp = api.requests.get(thumb_src)
    assert thumb_resp.status_code == 200


def test_can_lookup_document(api, png_file):
    data = {
        "title": "Hello world"
    }
    resp = api.requests.post("/upload", files={"file": png_file}, data=data)

    doc_id = resp.json()["id"]

    resp = api.requests.get(f"/documents/{doc_id}")
    assert resp.status_code == 200
    assert data["title"] == resp.json()["title"]


def test_lookup_missing_document_is_404(api):
    resp = api.requests.get("/documents/doesnotexist")
    assert resp.status_code == 404


def test_resolves_css(tagged_store, config):
    service.compile_css(accent_color="#ff0000")

    api = service.create_api(tagged_store, config=config)
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
    ("cluster.png", "filename*=utf-8''cluster.png"),
])
def test_sets_content_disposition_header(api, png_file, filename, expected_header):
    resp = api.requests.post(
        "/upload",
        files={"file": png_file},
        data={"filename": filename}
    )

    doc_id = resp.json()["id"]

    resp = api.requests.get(f"/documents/{doc_id}")

    file_identifier = resp.json()["file_identifier"]
    resp = api.requests.get(f"/files/{file_identifier}")
    assert resp.headers["Content-Disposition"] == expected_header


def test_does_not_set_content_disposition_if_no_filename(api, png_file):
    resp = api.requests.post("/upload", files={"file": png_file})

    doc_id = resp.json()["id"]
    resp = api.requests.get(f"/files/{doc_id[0]}/{doc_id}.png")
    assert "Content-Disposition" not in resp.headers


class TestBrowser:
    """Tests for the in-browser functionality"""

    @staticmethod
    def upload(api, file_contents, data=None, referer=None):
        data = data or {}
        referer = referer or "http://localhost:8072/"
        return api.requests.post(
            "/upload",
            files={"file": ("mydocument.png", file_contents, "image/png")},
            data=data,
            headers={"referer": referer}
        )

    def test_returns_302_redirect_to_original_page(self, api, png_file):
        original_page = "https://example.org/docstore/"
        resp = self.upload(api=api, file_contents=png_file, referer=original_page)

        assert resp.status_code == 302
        assert resp.headers["Location"].startswith(original_page)

    def test_includes_document_in_store(self, api, tagged_store, png_file):
        resp = self.upload(api=api, file_contents=png_file)

        location = hyperlink.URL.from_text(resp.headers["Location"])
        doc_id = dict(location.query)["_message.id"]

        stored_doc = tagged_store.objects[doc_id]
        assert stored_doc["filename"] == "mydocument.png"


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


@pytest.mark.parametrize("tag", ["x-y", "x-&-y"])
def test_can_navigate_to_tag(api, png_file, tag):
    # Regression test for https://github.com/alexwlchan/docstore/issues/60
    resp = api.requests.post(
        "/upload",
        files={"file": png_file},
        data={"tags": [tag], "title": "hello world"}
    )

    resp = api.requests.get("/")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    tag_div = soup.find("div", attrs={"id": "collapseTagList"})
    link_to_tag = tag_div.find("ul").find("li").find("a").attrs["href"]

    resp = api.requests.get("/" + link_to_tag)
    assert "hello world" in resp.text


def test_sets_caching_headers_on_file(api, png_file):
    resp = api.requests.post("/upload", files={"file": png_file})

    doc_id = resp.json()["id"]

    now = time.time()

    while time.time() - now < 5:  # pragma: no cover
        resp = api.requests.get(f"/documents/{doc_id}")

        if "thumbnail_identifier" in resp.json():
            break

    data = resp.json()

    file_resp = api.requests.head(f"/files/{data['file_identifier']}")
    assert file_resp.headers["Cache-Control"] == "public, max-age=31536000"

    thumb_resp = api.requests.head(f"/thumbnails/{data['thumbnail_identifier']}")
    assert thumb_resp.headers["Cache-Control"] == "public, max-age=31536000"


def test_can_filter_by_tag(api, tagged_store, file_manager):
    index_new_document(
        tagged_store,
        file_manager,
        doc_id="1",
        doc={
            "file": b"hello world",
            "title": "hello world",
            "tags": ["bar", "baz"]
        }
    )
    index_new_document(
        tagged_store,
        file_manager,
        doc_id="2",
        doc={
            "file": b"hi world",
            "title": "hi world",
            "tags": ["bar", "bat"]
        }
    )

    resp_bar = api.requests.get("/", params={"tag": "bar"})
    assert "hello world" in resp_bar.text
    assert "hi world" in resp_bar.text

    resp_bat = api.requests.get("/", params={"tag": ["bar", "bat"]})
    assert "hello world" not in resp_bat.text
    assert "hi world" in resp_bat.text


def test_uses_display_title(tagged_store, config):
    config.title = "this is my example instance"
    api = service.create_api(tagged_store, config=config)

    resp = api.requests.get("/")
    assert config.title in resp.text


class TestListView:
    @staticmethod
    def _assert_is_table(html):
        assert '<main class="documents documents__view_grid">' not in html
        assert '<main class="documents documents__view_table">' in html

    @staticmethod
    def _assert_is_grid(html):
        assert '<main class="documents documents__view_grid">' in html
        assert '<main class="documents documents__view_table">' not in html

    def test_can_set_default_table_view(self, config, tagged_store, file_manager):
        index_new_document(
            tagged_store,
            file_manager,
            doc_id="1",
            doc={"file": b"hello world", "title": "xyz"}
        )
        config.list_view = "table"

        api = service.create_api(tagged_store, config=config)
        resp = api.requests.get("/")
        self._assert_is_table(resp.text)

    def test_can_set_default_grid_view(self, config, tagged_store, file_manager):
        index_new_document(
            tagged_store,
            file_manager,
            doc_id="1",
            doc={"file": b"hello world", "title": "xyz"}
        )

        config.list_view = "grid"

        api = service.create_api(tagged_store, config=config)
        resp = api.requests.get("/")
        self._assert_is_grid(resp.text)

    def test_can_request__view_explicitly(self, api, png_file):
        api.requests.post(
            "/upload",
            files={"file": png_file},
            data={}
        )

        resp_grid = api.requests.get("/", params={"view": "grid"})
        self._assert_is_grid(resp_grid.text)

        resp_table = api.requests.get("/", params={"view": "table"})
        self._assert_is_table(resp_table.text)


class TestMigrations:
    def test_changes_checksums_to_sha256(self, store_root):
        json_string = json.dumps({
            "1": {"name": "alex"},
            "2": {"name": "lexie", "sha256_checksum": "abcdef"},
            "3": {"name": "carol", "sha256_checksum": "ghijkl", "checksum": "xyz"}
        })

        db_root = store_root / "documents.json"
        db_root.open("w").write(json_string)

        p = multiprocessing.Process(target=service.run_api, args=([str(store_root)], ))
        p.start()

        time.sleep(1)
        p.terminate()

        expected_data = {
            "1": {"name": "alex"},
            "2": {"name": "lexie", "checksum": "sha256:abcdef"},
            "3": {"name": "carol", "sha256_checksum": "ghijkl", "checksum": "xyz"}
        }

        actual_data = json.load(db_root.open())

        assert actual_data == expected_data
