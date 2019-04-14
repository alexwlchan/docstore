# -*- encoding: utf-8

import functools
from urllib.parse import quote as urlquote


@functools.lru_cache()
def remove_tag_from_url(tag, req_url):
    return req_url.remove(name="tag", value=urlquote(tag))
