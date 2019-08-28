# -*- encoding: utf-8

import math

import attr


@attr.s
class Pagination:
    page_size = attr.ib()
    current_page = attr.ib()
    total_documents = attr.ib()

    @property
    def total_pages(self):
        return int(math.ceil(self.total_documents / self.page_size))

    @property
    def has_next(self):
        return self.total_pages > self.current_page

    @property
    def next_page(self):
        if self.has_next:
            return self.current_page + 1
        else:
            raise ValueError("No next page!")

    @property
    def has_prev(self):
        return self.current_page > 1

    @property
    def prev_page(self):
        if self.has_prev:
            return self.current_page - 1
        else:
            raise ValueError("No previous page!")
