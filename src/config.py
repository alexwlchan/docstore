# -*- encoding: utf-8

import attr


@attr.s
class DocstoreConfig:
    root = attr.ib()
    title = attr.ib()
    list_view = attr.ib()
    tag_view = attr.ib()
    accent_color = attr.ib()
    page_size = attr.ib(converter=int)
