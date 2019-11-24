# -*- encoding: utf-8

import io

import bs4
import hyperlink
import pytest

import css
from file_manager import FileManager
import helpers
from index_helpers import index_new_document


def test_non_post_to_upload_is_405(app):
    resp = app.get("/upload")
    assert resp.status_code == 405


@pytest.mark.parametrize("data", [
    {},
    {"name": "lexie"},
    {"ffffile": (b"hello world", "greeting.txt")},
])
def test_no_file_data_is_400(app, data):
    resp = app.post("/upload", data=data)
    assert resp.status_code == 400
    assert resp.json == {"error": "No file in upload?"}


@pytest.mark.parametrize("data", [
    {},
    {"title": "Hello world"},
    {"tags": ["cluster"]},
    {"filename": "cluster.png"},
])
def test_can_upload_without_all_parameters(app, data):
    data["file"] = (io.BytesIO(b"hello world"), "greeting.txt")
    resp = app.post("/upload", data=data)
    print(resp.json)
    assert resp.status_code == 201
    assert resp.json.keys() == {"id"}


def test_stores_document_in_store(app, tagged_store, png_path):
    data = {
        "title": "Hello world",
        "tags": "cluster elasticsearch blue",
        "file": (io.BytesIO(b"hello world"), "greeting.txt")
    }
    resp = app.post("/upload", data=data)
    assert resp.status_code == 201
    assert list(resp.json.keys()) == ["id"]

    docid = resp.json["id"]
    stored_doc = tagged_store.objects[docid]
    assert stored_doc["title"] == data["title"]
    assert stored_doc["tags"] == data["tags"].split()
    assert stored_doc["filename"] == "greeting.txt"
    assert "checksum" in stored_doc


def test_extra_keys_are_kept_in_store(app, tagged_store):
    data = {
        "key1": "value1",
        "key2": "value2",
        "file": (io.BytesIO(b"hello world"), "greeting.txt"),
    }
    resp = app.post("/upload", data=data)
    assert resp.status_code == 201
    assert list(resp.json.keys()) == ["id"]

    docid = resp.json["id"]
    stored_doc = tagged_store.objects[docid]
    assert stored_doc["user_data"] == {
        "key1": "value1",
        "key2": "value2",
    }


def test_calls_create_thumbnail(app, tagged_store, png_file):
    resp = app.post(
        "/upload",
        data={"file": (png_file, "cluster.png")}
    )
    assert resp.status_code == 201
    doc_id = resp.json["id"]

    stored_doc = tagged_store.objects[doc_id]
    assert "thumbnail_identifier" in stored_doc


def test_get_view_endpoint(app):
    data = {
        "title": "Hello world",
        "file": (io.BytesIO(b"hello world"), "greeting.txt")
    }
    app.post("/upload", data=data)

    resp = app.get("/")
    assert resp.status_code == 200
    assert b"Hello world" in resp.data


def test_can_view_file_and_thumbnail(app, png_file, png_path):
    app.post("/upload", data={"file": (png_file, "cluster.png")})

    resp = app.get("/")
    assert resp.status_code == 200

    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    all_links = soup.find_all("a", attrs={"target": "_blank"})
    png_links = list(set(
        link.attrs["href"]
        for link in all_links
        if link.attrs.get("href", "").endswith(".png")
    ))
    assert len(png_links) == 1
    png_href = png_links[0]

    print(png_href)

    png_resp = app.get("/" + png_href)
    assert png_resp.status_code == 200
    assert png_resp.data == open(png_path, "rb").read()

    thumbnails_div = soup.find_all("div", attrs={"class": "document__image"})
    assert len(thumbnails_div) == 1
    thumbnails_img = thumbnails_div[0].find_all("img")
    assert len(thumbnails_img) == 1
    thumb_src = thumbnails_img[0].attrs["src"]

    thumb_resp = app.get("/" + thumb_src)
    assert thumb_resp.status_code == 200


def test_can_view_existing_file_and_thumbnail(
    tagged_store, store_root, png_file, png_path
):
    app = helpers.create_app(
        tagged_store=tagged_store,
        store_root=store_root
    )

    app.post("/upload", data={"file": (png_file, "cluster.png")})

    new_app = helpers.create_app(
        tagged_store=tagged_store,
        store_root=store_root
    )

    resp = new_app.get("/")
    assert resp.status_code == 200

    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    all_links = soup.find_all("a", attrs={"target": "_blank"})
    png_links = list(set(
        link.attrs["href"]
        for link in all_links
        if link.attrs.get("href", "").endswith(".png")
    ))
    assert len(png_links) == 1
    png_href = png_links[0]

    png_resp = new_app.get("/" + png_href)
    assert png_resp.status_code == 200
    assert png_resp.data == open(png_path, "rb").read()

    thumbnails_div = soup.find_all("div", attrs={"class": "document__image"})
    assert len(thumbnails_div) == 1
    thumbnails_img = thumbnails_div[0].find_all("img")
    assert len(thumbnails_img) == 1
    thumb_src = thumbnails_img[0].attrs["src"]

    thumb_resp = app.get("/" + thumb_src)
    assert thumb_resp.status_code == 200


def test_can_lookup_document(app, png_file):
    data = {
        "title": "Hello world",
        "file": (io.BytesIO(b"hello world"), "greeting.txt")
    }
    resp = app.post("/upload", data=data)

    doc_id = resp.json["id"]

    resp = app.get(f"/documents/{doc_id}")
    assert resp.status_code == 200
    assert data["title"] == resp.json["title"]


def test_lookup_missing_document_is_404(app):
    resp = app.get("/documents/doesnotexist")
    assert resp.status_code == 404


def test_resolves_css(tagged_store, store_root):
    css.compile_css(accent_color="#ff0000")

    app = helpers.create_app()

    resp = app.get("/")
    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    css_links = [
        link.attrs["href"]
        for link in soup.find_all("link", attrs={"rel": "stylesheet"})
    ]

    local_links = [link for link in css_links if not link.startswith("https://")]
    assert len(local_links) == 1
    css_link = local_links[0]

    assert css_link.endswith(".css")
    css_resp = app.head(css_link)
    assert css_resp.status_code == 200


@pytest.mark.parametrize("filename,expected_header", [
    ("cluster.png", "filename*=utf-8''cluster.png"),
])
def test_sets_content_disposition_header(app, png_file, filename, expected_header):
    resp = app.post(
        "/upload",
        data={"file": (png_file, filename)}
    )

    doc_id = resp.json["id"]

    resp = app.get(f"/documents/{doc_id}")

    file_identifier = resp.json["file_identifier"]
    resp = app.get(f"/files/{file_identifier}")
    assert resp.status_code == 200
    assert resp.headers["Content-Disposition"] == expected_header


def test_does_not_set_content_disposition_if_no_filename(store_root, tagged_store):
    file_manager = FileManager(store_root / "files")

    doc = index_new_document(
        tagged_object_store=tagged_store,
        file_manager=file_manager,
        doc_id="1",
        doc={"file": b"hello world", "title": "greeting"}
    )

    app = helpers.create_app(
        tagged_store=tagged_store,
        store_root=store_root
    )

    resp = app.get(f"/files/{doc['file_identifier']}")
    assert resp.status_code == 200
    assert "Content-Disposition" not in resp.headers


class TestBrowser:
    """Tests for the in-browser functionality"""

    @staticmethod
    def upload(app, file_contents, data=None, referer=None):
        data = data or {}
        referer = referer or "http://localhost:8072/"

        data["file"] = (file_contents, "mydocument.png")

        return app.post("/upload", data=data, headers={"referer": referer})

    def test_returns_302_redirect_to_original_page(self, app, png_file):
        original_page = "https://example.org/docstore/"
        resp = self.upload(app=app, file_contents=png_file, referer=original_page)

        assert resp.status_code == 302
        assert resp.headers["Location"].startswith(original_page)

    def test_includes_document_in_store(self, app, tagged_store, png_file):
        resp = self.upload(app=app, file_contents=png_file)

        location = hyperlink.URL.from_text(resp.headers["Location"])
        doc_id = dict(location.query)["_message.id"]

        stored_doc = tagged_store.objects[doc_id]
        assert stored_doc["filename"] == "mydocument.png"


@pytest.mark.parametrize("tag", ["x-y", "x-&-y"])
def test_can_navigate_to_tag(tag):
    # Regression test for https://github.com/alexwlchan/docstore/issues/60
    app = helpers.create_app(tag_view="list")
    resp = app.post(
        "/upload",
        data={
            "tags": [tag],
            "title": "hello world",
            "file": (io.BytesIO(b"hello world"), "greeting.txt")
        }
    )

    resp = app.get("/")
    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    tag_div = soup.find("div", attrs={"id": "collapseTagList"})
    link_to_tag = tag_div.find("ul").find("li").find("a").attrs["href"]

    resp = app.get("/" + link_to_tag)
    assert b"hello world" in resp.data


def test_sets_caching_headers_on_file(app, png_file):
    resp = app.post("/upload", data={"file": (png_file, "cluster.png")})

    doc_id = resp.json["id"]

    resp = app.get(f"/documents/{doc_id}")

    file_resp = app.get(f"/files/{resp.json['file_identifier']}")
    assert file_resp.status_code == 200
    assert file_resp.headers["Cache-Control"] == "public, max-age=31536000"

    thumb_resp = app.head(f"/thumbnails/{resp.json['thumbnail_identifier']}")
    assert file_resp.status_code == 200
    assert thumb_resp.headers["Cache-Control"] == "public, max-age=31536000"


def test_can_filter_by_tag(tagged_store, file_manager):
    app = helpers.create_app(tagged_store=tagged_store)

    index_new_document(
        tagged_store,
        file_manager,
        doc_id="1",
        doc={
            "file": b"1234",
            "title": "hello world",
            "tags": ["x", "y"]
        }
    )
    index_new_document(
        tagged_store,
        file_manager,
        doc_id="2",
        doc={
            "file": b"5678",
            "title": "hi world",
            "tags": ["x", "z"]
        }
    )

    resp_tag_x = app.get(
        "/", query_string=[("tag", "x")]
    )
    html_x_bytes = resp_tag_x.data
    assert b"hello world" in html_x_bytes
    assert b"hi world" in html_x_bytes

    resp_tag_x_y = app.get(
        "/", query_string=[("tag", "x"), ("tag", "y")]
    )
    html_x_y_bytes = resp_tag_x_y.data
    assert b"hello world" in html_x_y_bytes
    assert b"hi world" not in html_x_y_bytes


def test_uses_display_title():
    title = "My docstore title"

    app = helpers.create_app(title=title)

    resp = app.get("/")

    assert b"My docstore title" in resp.data


class TestListView:
    @staticmethod
    def _assert_is_table(resp):
        html_bytes = resp.data
        assert b'<main class="documents documents__view_grid">' not in html_bytes
        assert b'<main class="documents documents__view_table">' in html_bytes

    @staticmethod
    def _assert_is_grid(resp):
        html_bytes = resp.data
        assert b'<main class="documents documents__view_grid">' in html_bytes
        assert b'<main class="documents documents__view_table">' not in html_bytes

    def test_can_set_default_table_view(self, tagged_store, file_manager):
        index_new_document(
            tagged_store,
            file_manager,
            doc_id="1",
            doc={
                "file": b"hello world",
                "title": "xyz"
            }
        )

        app = helpers.create_app(
            tagged_store=tagged_store,
            list_view="table"
        )

        resp = app.get("/")
        self._assert_is_table(resp)

    def test_can_set_default_grid_view(self, tagged_store, file_manager):
        index_new_document(
            tagged_store,
            file_manager,
            doc_id="1",
            doc={
                "file": b"hello world",
                "title": "xyz"
            }
        )

        app = helpers.create_app(
            tagged_store=tagged_store,
            list_view="grid"
        )

        resp = app.get("/")
        self._assert_is_grid(resp)


def test_default_sort_is_newest_first(app):
    for title in ("xyz_1", "abc_2", "mno_3"):
        app.post(
            "/upload",
            data={
                "title": title,
                "file": (io.BytesIO(b"hello world"), "greeting.txt")
            }
        )

    resp = app.get("/")
    html_soup = bs4.BeautifulSoup(resp.data, "html.parser")

    titles = [
        div.text.strip()
        for div in html_soup.find_all("div", attrs={"class": "document__title"})
    ]

    assert titles == ["mno_3", "abc_2", "xyz_1"]


@pytest.mark.parametrize("sort_by, expected_titles", [
    ("title:a_z", ["abc_2", "mno_3", "xyz_1"]),
    ("title:z_a", ["xyz_1", "mno_3", "abc_2"]),
    ("date_created:newest_first", ["mno_3", "abc_2", "xyz_1"]),
    ("date_created:oldest_first", ["xyz_1", "abc_2", "mno_3"]),
])
def test_respects_sort_order(app, sort_by, expected_titles):
    # The sort order of titles should be different to the sort order
    # by date.
    for title in ("xyz_1", "abc_2", "mno_3"):
        app.post(
            "/upload",
            data={
                "title": title,
                "file": (io.BytesIO(b"hello world"), "greeting.txt")
            }
        )

    resp = app.get("/", query_string={"sort": sort_by})

    html_soup = bs4.BeautifulSoup(resp.data, "html.parser")

    titles = [
        div.text.strip()
        for div in html_soup.find_all("div", attrs={"class": "document__title"})
    ]

    assert titles == expected_titles


@pytest.mark.parametrize("sort_by", [
    "title:ascending",
    "date_created:descending",
    "ascending",
    "x:y:z",
])
def test_invalid_sort_params_are_rejected(app, sort_by):
    resp = app.get("/", query_string={"sort": sort_by})

    assert resp.status_code == 400
    assert resp.json == {"error": f"Unrecognised sort parameter: {sort_by}"}


class TestCookies:
    """Test the use of cookies to collapse/expand certain areas."""

    def test_document_form_is_collapsed_by_default(self, app):
        resp = app.get("/")

        html_soup = bs4.BeautifulSoup(resp.data, "html.parser")

        div = html_soup.find("div", attrs={"id": "collapseDocumentForm"})
        assert div.attrs["class"] == ["collapse"]

    @pytest.mark.parametrize("cookie_value, expected_classes", [
        ("true", ["collapse", "show"]),
        ("false", ["collapse"]),
    ])
    def test_form_collapse_show_expands_document_form(
        self, app, cookie_value, expected_classes
    ):
        app.set_cookie("localhost", "form-collapse__show", cookie_value)
        resp = app.get("/")

        html_soup = bs4.BeautifulSoup(resp.data, "html.parser")

        div = html_soup.find("div", attrs={"id": "collapseDocumentForm"})
        assert div.attrs["class"] == expected_classes

    def test_tag_browser_is_collapsed_by_default(self, app):
        app.post(
            "/upload",
            data={
                "tags": "alfa bravo charlie",
                "file": (io.BytesIO(b"hello world"), "greeting.txt")
            }
        )

        resp = app.get("/")

        html_soup = bs4.BeautifulSoup(resp.data, "html.parser")

        div = html_soup.find("div", attrs={"id": "collapseTagList"})
        assert div.attrs["class"] == ["collapse"]

    @pytest.mark.parametrize("cookie_value, expected_classes", [
        ("true", ["collapse", "show"]),
        ("false", ["collapse"]),
    ])
    def test_form_collapse_show_expands_tag_browser(
        self, app, cookie_value, expected_classes
    ):
        app.post(
            "/upload",
            data={
                "tags": "alfa bravo charlie",
                "file": (io.BytesIO(b"hello world"), "greeting.txt")
            }
        )

        app.set_cookie("localhost", "tags-collapse__show", cookie_value)
        resp = app.get("/")

        html_soup = bs4.BeautifulSoup(resp.data, "html.parser")

        div = html_soup.find("div", attrs={"id": "collapseTagList"})
        assert div.attrs["class"] == expected_classes


class TestPagination:
    def test_only_gets_documents_for_page(self, app):
        for i in range(1, 11):
            app.post(
                "/upload",
                data={
                    "title": f"document {i}",
                    "file": (io.BytesIO(b"hello world"), "greeting.txt")
                }
            )

        resp = app.get("/", query_string={"page": 1, "page_size": 5})
        html_soup = bs4.BeautifulSoup(resp.data, "html.parser")
        assert str(html_soup) != "null"

        titles = [
            div.text.strip()
            for div in html_soup.find_all("div", attrs={"class": "document__title"})
        ]

        assert titles == [
            "document 10",
            "document 9",
            "document 8",
            "document 7",
            "document 6"
        ]

        assert html_soup.find("nav", attrs={"id": "pagination"}) is not None

    @pytest.mark.parametrize("page_size", [1, 5, 20])
    def test_uses_page_size(self, page_size):
        app = helpers.create_app(page_size=page_size)

        for i in range(1, 25):
            app.post(
                "/upload",
                data={
                    "title": f"document {i}",
                    "file": (io.BytesIO(b"hello world"), "greeting.txt")
                }
            )

        resp = app.get("/")
        html_soup = bs4.BeautifulSoup(resp.data, "html.parser")
        assert str(html_soup) != "null"

        titles = [
            div.text.strip()
            for div in html_soup.find_all("div", attrs={"class": "document__title"})
        ]

        assert len(titles) == page_size
