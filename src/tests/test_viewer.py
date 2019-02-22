# -*- encoding: utf-8

import pytest

from index_helpers import index_document


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
    index_document(store=store, user_data={"file": b"hello world", "title": "foo"})
    resp = sess.get("/", params={"view": "table"})
    assert '<div class="row">' not in resp.text
    assert '<table class="table">' in resp.text


def test_grid_view(sess, store):
    index_document(store=store, user_data={"file": b"hello world", "title": "foo"})
    resp = sess.get("/", params={"view": "grid"})
    assert '<div class="row">' in resp.text
    assert '<table class="table">' not in resp.text
