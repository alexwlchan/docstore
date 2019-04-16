# -*- encoding: utf-8

import bs4
import pytest

import api as service
from index_helpers import index_document


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

    api.requests.hooks["response"].append(raise_for_status)
    return api.requests


def test_empty_state(sess):
    resp = sess.get("/")
    assert "No documents found" in resp.text
    assert '<div class="row">' not in resp.text
    assert '<table class="table">' not in resp.text


def test_table_view(sess, store):
    index_document(store=store, user_data={
        "file": b"hello world",
        "title": "foo",
        "tags": ["bar", "baz", "bat"]
    })
    resp = sess.get("/", params={"view": "table"})
    assert '<div class="row">' not in resp.text
    assert '<table class="table">' in resp.text


def test_grid_view(sess, store):
    index_document(store=store, user_data={"file": b"hello world", "title": "foo"})
    resp = sess.get("/", params={"view": "grid"})
    assert '<div class="row">' in resp.text
    assert '<table class="table">' not in resp.text


def test_uses_display_title(store):
    resp = service.create_api(store).requests.get("/")
    assert "Alex’s documents" in resp.text

    resp = service.create_api(store, display_title="Manuals").requests.get("/")
    assert "Manuals" in resp.text


def test_can_filter_by_tag(sess, store):
    index_document(
        store=store,
        user_data={
            "file": b"hello world",
            "title": "hello world",
            "tags": ["bar", "baz"]
        }
    )
    index_document(
        store=store,
        user_data={
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
    index_document(
        store=store,
        user_data={
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
    index_document(
        store=store,
        user_data={
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
