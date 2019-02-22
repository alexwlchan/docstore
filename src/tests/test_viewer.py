# -*- encoding: utf-8

import pytest


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
