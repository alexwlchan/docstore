# -*- encoding: utf-8

import hyperlink
import pytest

import urls


@pytest.mark.parametrize("url,new_tag,expected_url", [
    ("http://localhost:8072/", "x", "?tag=x"),
    ("http://localhost:8072/?tag=y", "x", "?tag=y&tag=x"),
    ("http://localhost:8072/", "Niño", "?tag=Ni%C3%B1o"),
])
def test_add_tag_to_url(url, new_tag, expected_url):
    req_url = hyperlink.URL.from_text(url)
    assert urls.add_tag_to_url(new_tag, req_url=req_url) == expected_url


@pytest.mark.parametrize("url,tag,expected_url", [
    ("http://localhost:8072/?tag=x&tag=y", "x", "?tag=y"),
    ("http://localhost:8072/?tag=Ni%C3%B1o", "Niño", "?"),
])
def test_remove_tag_from_url(url, tag, expected_url):
    req_url = hyperlink.URL.from_text(url)
    assert urls.remove_tag_from_url(tag, req_url=req_url) == expected_url
