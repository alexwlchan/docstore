# -*- encoding: utf-8

import functools
from urllib.parse import quote as urlquote


@functools.lru_cache()
def add_tag_to_url(tag, req_url):
    quoted_tag = urlquote(tag)
    assert quoted_tag not in req_url.get("tag")
    return req_url.add("tag", quoted_tag)


@functools.lru_cache()
def remove_tag_from_url(tag, req_url):
    return req_url.remove(name="tag", value=urlquote(tag))
