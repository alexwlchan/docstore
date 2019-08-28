# -*- encoding: utf-8

import pytest

from pagination import Pagination


@pytest.mark.parametrize("page_size, total_documents, total_pages", [
    (1, 20, 20),
    (3, 20, 7),
    (25, 20, 1),
])
def test_total_pages(page_size, total_documents, total_pages):
    p = Pagination(page_size=page_size, current_page=1, total_documents=total_documents)
    assert p.total_pages == total_pages


def test_next_page():
    p = Pagination(
        page_size=10,
        current_page=1,
        total_documents=20
    )

    assert p.next_page == 2


def test_next_page_if_invalid_is_error():
    p = Pagination(
        page_size=10,
        current_page=1,
        total_documents=5
    )

    with pytest.raises(ValueError, match="No next page!"):
        p.next_page


@pytest.mark.parametrize("page_size, current_page, total_documents, prev_page", [
    (10, 2, 20, 1),
])
def test_prev_page(page_size, current_page, total_documents, prev_page):
    p = Pagination(
        page_size=page_size,
        current_page=current_page,
        total_documents=total_documents
    )

    assert p.prev_page == prev_page


def test_prev_page_if_invalid_is_error():
    p = Pagination(
        page_size=10,
        current_page=1,
        total_documents=5
    )

    with pytest.raises(ValueError, match="No previous page!"):
        p.prev_page
