# -*- encoding: utf-8

import hyperlink
import pytest

import urls


@pytest.mark.parametrize("url,tag,expected_url", [
    ("http://localhost:8072/?tag=x&tag=y", "x", "http://localhost:8072/?tag=y"),
    ("http://localhost:8072/?tag=Ni%C3%B1o", "Niño", "http://localhost:8072/"),
])
def test_remove_tag_from_url(url, tag, expected_url):
    req_url = hyperlink.URL.from_text(url)
    expected_result = hyperlink.URL.from_text(expected_url)
    assert urls.remove_tag_from_url(tag, req_url=req_url) == expected_result
