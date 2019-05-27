# -*- encoding: utf-8

import re

import bs4
import pytest

import api as service
from index_helpers import index_new_document


PARAMS = [
    [("view", "table"), ("tag", "x")],
    [("sort", "title:asc")],
    [("sort", "title:desc")],
    [("sort", "date_created:asc")],
    [("sort", "date_created:desc")],
]


@pytest.fixture
def sess(api):
    def raise_for_status(resp, *args, **kwargs):
        resp.raise_for_status()
        assert resp.text != "null"

    api.requests.hooks["response"].append(raise_for_status)
    return api.requests


def test_empty_state(sess):
    resp = sess.get("/")
    assert "No documents found" in resp.text
    assert '<div class="row">' not in resp.text
    assert '<table class="table">' not in resp.text


class TestViewOptions:

    @staticmethod
    def _assert_is_table(resp):
        assert '<div class="row">' not in resp.text
        assert '<table class="table">' in resp.text

    @staticmethod
    def _assert_is_grid(resp):
        assert '<div class="row">' in resp.text
        assert '<table class="table">' not in resp.text

    def test_table_view(self, sess, store):
        index_new_document(store=store, doc_id="1", doc={
            "file": b"hello world",
            "title": "foo",
            "tags": ["bar", "baz", "bat"]
        })
        resp = sess.get("/", params={"view": "table"})
        self._assert_is_table(resp)

    def test_grid_view(self, sess, store):
        index_new_document(
            store=store,
            doc_id="1",
            doc={"file": b"hello world", "title": "foo"}
        )
        resp = sess.get("/", params={"view": "grid"})
        self._assert_is_grid(resp)

    def test_default_is_table_view(self, store):
        index_new_document(
            store=store,
            doc_id="1",
            doc={"file": b"hello world", "title": "xyz"}
        )
        api = service.create_api(store)
        resp = api.requests.get("/")
        self._assert_is_table(resp)

    def test_can_set_default_as_table_view(self, store):
        index_new_document(
            store=store,
            doc_id="1",
            doc={"file": b"hello world", "title": "xyz"}
        )
        api = service.create_api(store, default_view="table")
        resp = api.requests.get("/")
        self._assert_is_table(resp)

    def test_can_set_default_as_grid_view(self, store):
        index_new_document(
            store=store,
            doc_id="1",
            doc={"file": b"hello world", "title": "xyz"}
        )
        api = service.create_api(store, default_view="grid")
        resp = api.requests.get("/")
        self._assert_is_grid(resp)


def test_uses_display_title(store):
    resp = service.create_api(store).requests.get("/")
    assert "Alex’s documents" in resp.text

    resp = service.create_api(store, display_title="Manuals").requests.get("/")
    assert "Manuals" in resp.text


def test_can_filter_by_tag(sess, store):
    index_new_document(
        store=store,
        doc_id="1",
        doc={
            "file": b"hello world",
            "title": "hello world",
            "tags": ["bar", "baz"]
        }
    )
    index_new_document(
        store=store,
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


@pytest.mark.parametrize("params", PARAMS)
def test_shows_column_headers(sess, store, params):
    index_new_document(
        store=store,
        doc_id="1",
        doc={
            "file": b"hello world",
            "title": "hello world",
            "tags": ["x", "y"]
        }
    )

    resp = sess.get("/", params=params)
    assert "Date saved" in resp.text
    assert "Name" in resp.text
    assert resp.text.count("&Darr;") <= 1
    assert resp.text.count("&Uarr;") <= 1
    assert resp.text.count("&Darr;") + resp.text.count("&Uarr;") == 1


@pytest.mark.parametrize("params", PARAMS)
def test_all_urls_are_relative(sess, store, params):
    index_new_document(
        store=store,
        doc_id="1",
        doc={
            "file": b"hello world",
            "title": "hello world",
            "tags": ["x", "y"]
        }
    )

    resp = sess.get("/", params=params)

    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    links = [a.attrs["href"] for a in soup.find_all("a")]

    for href in links:
        assert href.startswith(("?", "#", "files/")), href


def test_version_is_shown_in_footer(sess):
    resp = sess.get("/")

    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    footer = soup.find("footer")

    assert re.search(r'docstore v\d+\.\d+\.\d+', str(footer)) is not None


def test_includes_created_date(store, sess):
    index_new_document(
        store=store,
        doc_id="1",
        doc={
            "file": b"hello world",
            "title": "hello world"
        }
    )

    resp = sess.get("/")

    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    date_created_td = soup.find("td", attrs={"class": "date__created"})
    assert date_created_td.text == "just now"


class TestStoreDocumentForm:
    def test_url_decodes_tags_before_displaying(self, sess, pdf_file):
        """
        Check that URL-encoded entities get unwrapped when we display the tag form.

        e.g. "colour:blue" isn't displayed as "colour%3Ablue"

        """
        sess.post(
            "/upload",
            files={"file": ("mydocument.pdf", pdf_file)},
            data={"tags": ["colour:blue"]}
        )

        resp = sess.get("/", params={"tag": "colour:blue"})

        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        tag_field = soup.find("input", attrs={"name": "tags"})
        assert tag_field.attrs["value"] == "colour:blue"


def test_omits_source_url_if_empty(sess, pdf_file):
    sess.post(
        "/upload",
        files={"file": ("mydocument.pdf", pdf_file)},
        data={"title": "my great document", "source_url": ""}
    )

    resp = sess.get("/")

    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    assert len(soup.find_all("tr")) == 2  # header + single row
    assert soup.find("span", attrs={"class": "source_url"}) is None
