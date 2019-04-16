# -*- encoding: utf-8

import functools
from urllib.parse import quote as urlquote


def _build_query(url):
    return "?" + "&".join(f"{k}={v}" for k, v in url.query)


@functools.lru_cache()
def add_tag_to_url(tag, req_url):
    quoted_tag = urlquote(tag)
    assert quoted_tag not in req_url.get("tag")
    return _build_query(req_url.add("tag", quoted_tag))


@functools.lru_cache()
def remove_tag_from_url(tag, req_url):
    return _build_query(req_url.remove(name="tag", value=urlquote(tag)))


def set_sort_order(sort_order, req_url):
    return _build_query(req_url.set("sort", sort_order))


def set_view_option(view_option, req_url):
    return _build_query(req_url.set("view", view_option))
