# -*- encoding: utf-8

import datetime as dt
import re
import time

import bs4
import pytest

import api as service
from index_helpers import index_new_document
import viewer


PARAMS = [
    [("view", "table"), ("tag", "x")],
    [("sort", "title:asc")],
    [("sort", "title:desc")],
    [("sort", "date_created:asc")],
    [("sort", "date_created:desc")],
]


def get_html(
    documents=[],
    view_options=viewer.ViewOptions(),
    api_version="test_1.0.0"
):
    return viewer.render_document_list(
        documents=documents,
        view_options=view_options,
        api_version=api_version
    )


def get_html_soup(**kwargs):
    html = get_html(**kwargs)

    return bs4.BeautifulSoup(html, "html.parser")


@pytest.fixture
def sess(api):
    def raise_for_status(resp, *args, **kwargs):
        resp.raise_for_status()
        assert resp.text != "null"

    api.requests.hooks["response"].append(raise_for_status)
    return api.requests


def test_empty_state():
    html = get_html(documents=[])

    assert "No documents found" in html
    assert '<div class="row">' not in html
    assert '<table class="table">' not in html


class TestViewOptions:

    @staticmethod
    def _assert_is_table(html):
        assert '<main class="documents documents__view_grid">' not in html
        assert '<main class="documents documents__view_table">' in html

    @staticmethod
    def _assert_is_grid(html):
        assert '<main class="documents documents__view_grid">' in html
        assert '<main class="documents documents__view_table">' not in html

    def test_table_view(self, document):
        html = get_html(
            documents=[document],
            view_options=viewer.ViewOptions(list_view="table")
        )

        self._assert_is_table(html)

    def test_grid_view(self, document):
        html = get_html(
            documents=[document],
            view_options=viewer.ViewOptions(list_view="grid")
        )

        self._assert_is_grid(html)

    def test_default_is_table_view(self, document):
        html = get_html(
            documents=[document],
            view_options=viewer.ViewOptions()
        )

        self._assert_is_table(html)

    def test_can_set_default_table_view(self, store_root, tagged_store, file_manager):
        index_new_document(
            tagged_store,
            file_manager,
            doc_id="1",
            doc={"file": b"hello world", "title": "xyz"}
        )
        api = service.create_api(tagged_store, store_root, default_view="table")
        resp = api.requests.get("/")
        self._assert_is_table(resp)

    def test_can_set_default_grid_view(self, store_root, tagged_store, file_manager):
        index_new_document(
            tagged_store,
            file_manager,
            doc_id="1",
            doc={"file": b"hello world", "title": "xyz"}
        )
        api = service.create_api(tagged_store, store_root, default_view="grid")
        resp = api.requests.get("/")
        self._assert_is_grid(resp)


def test_uses_display_title(tagged_store, store_root):
    api = service.create_api(tagged_store, store_root)
    resp = api.requests.get("/")
    assert "docstore" in resp.text

    api = service.create_api(tagged_store, store_root, display_title="Manuals")
    resp = api.requests.get("/")
    assert "Manuals" in resp.text


def test_can_filter_by_tag(sess, tagged_store, file_manager):
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

    resp_bar = sess.get("/", params={"tag": "bar"})
    assert "hello world" in resp_bar.text
    assert "hi world" in resp_bar.text

    resp_bat = sess.get("/", params={"tag": ["bar", "bat"]})
    assert "hello world" not in resp_bat.text
    assert "hi world" in resp_bat.text


# TODO: Pass proper params here
@pytest.mark.parametrize("params", PARAMS)
def test_all_urls_are_relative(document, params):
    document["tags"] = ["x", "y"]

    html_soup = get_html_soup(documents=[document])
    links = [a.attrs["href"] for a in html_soup.find("main").find_all("a")]

    for href in links:
        assert href.startswith(("?", "#", "files/")), href


def test_version_is_shown_in_footer():
    html_soup = get_html_soup(api_version="1.2.3")
    footer = html_soup.find("footer")
    assert re.search(r'docstore v1\.2\.3', str(footer)) is not None


def test_includes_created_date(document):
    document["created_date"] = dt.datetime.now().isoformat()

    html_soup = get_html_soup(documents=[document])
    date_created_div = html_soup.find(
        "div", attrs={"class": "document__metadata__date_created"})
    assert date_created_div.find(
        "h5", attrs={"class": "document__metadata__info"}).text == "just now"


class TestStoreDocumentForm:
    def test_url_decodes_tags_before_displaying(self, document):
        """
        Check that URL-encoded entities get unwrapped when we display the tag form.

        e.g. "colour:blue" isn't displayed as "colour%3Ablue"

        """
        document["tags"] = ["colour:blue"]

        html_soup = get_html_soup(
            documents=[document],
            view_options=viewer.ViewOptions(tag_filter=["colour:blue"])
        )
        tag_field = html_soup.find("input", attrs={"name": "tags"})
        assert tag_field.attrs["value"] == "colour:blue"


def test_omits_source_url_if_empty(document):
    document["source_url"] = ""

    html_soup = get_html_soup(documents=[document])
    assert len(html_soup.find_all("section")) == 1
    assert html_soup.find("div", attrs={"id": "document__metadata__source_url"}) is None


@pytest.mark.parametrize("tag", ["x-y", "x-&-y"])
def test_can_navigate_to_tag(sess, pdf_file, tag):
    # Regression test for https://github.com/alexwlchan/docstore/issues/60
    resp = sess.post(
        "/upload",
        files={"file": ("mydocument.pdf", pdf_file)},
        data={"tags": [tag], "title": "hello world"}
    )

    resp = sess.get("/")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    tag_div = soup.find("div", attrs={"id": "collapseTagList"})
    link_to_tag = tag_div.find("ul").find("li").find("a").attrs["href"]

    resp = sess.get("/" + link_to_tag)
    assert "hello world" in resp.text


def test_renders_titles_with_pretty_quotes(document):
    document["title"] = "Isn't it a wonderful day? -- an optimist"

    html_soup = get_html_soup(documents=[document])
    title = html_soup.find("div", attrs={"class": "document__title"})
    assert "Isn’t it a wonderful day? — an optimist" in title.text


def test_sets_caching_headers_on_file(sess, pdf_file):
    resp = sess.post(
        "/upload",
        files={"file": ("mydocument.pdf", pdf_file)}
    )

    doc_id = resp.json()["id"]

    now = time.time()

    while time.time() - now < 5:  # pragma: no cover
        resp = sess.get(f"/documents/{doc_id}")

        if "thumbnail_identifier" in resp.json():
            break

    data = resp.json()

    file_resp = sess.head(f"/files/{data['file_identifier']}")
    assert file_resp.headers["Cache-Control"] == "public, max-age=31536000"

    thumb_resp = sess.head(f"/thumbnails/{data['thumbnail_identifier']}")
    assert thumb_resp.headers["Cache-Control"] == "public, max-age=31536000"
