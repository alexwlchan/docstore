from datetime import datetime

import pytest

from docstore.text_utils import common_prefix, pretty_date, slugify


@pytest.mark.parametrize(
    "values, expected_prefix",
    [
        (["My document"], "My document"),
        (["My document", "A different document"], ""),
        (["My document (1)", "My document (2)"], "My document"),
        (["My document (part 1)", "My document (part 2)"], "My document"),
        (["My document - part ", "My document - part 2"], "My document"),
    ],
)
def test_common_prefix(values, expected_prefix):
    assert common_prefix(values) == expected_prefix


@pytest.mark.parametrize(
    "u, expected_slug",
    [
        ("abc", "abc"),
        ("a:b", "a-b"),
        ("Çingleton", "cingleton"),
        ("a b", "a-b"),
        ("a_b", "a-b"),
        ("a  b", "a-b"),
    ],
)
def test_slugify(u, expected_slug):
    assert slugify(u) == expected_slug


@pytest.mark.parametrize(
    "d, now, expected_str",
    [
        (datetime(2001, 1, 1, 1, 1, 1), datetime(2001, 1, 1, 1, 1, 11), "just now"),
        (datetime(2001, 1, 1, 1, 1, 1), datetime(2001, 1, 1, 1, 2, 59), "just now"),
        (datetime(2001, 1, 1, 1, 1, 1), datetime(2001, 1, 1, 1, 3, 1), "2 minutes ago"),
        (datetime(2001, 1, 1, 1, 1, 1), datetime(2001, 1, 1, 3, 1, 1), "earlier today"),
        (datetime(2001, 1, 1, 1, 1, 1), datetime(2001, 1, 2, 1, 1, 1), "yesterday"),
        (datetime(2001, 1, 1, 1, 1, 1), datetime(2001, 1, 6, 1, 1, 1), "5 days ago"),
        (datetime(2001, 1, 1, 1, 1, 1), datetime(2001, 1, 12, 1, 1, 1), "1 Jan 2001"),
    ],
)
def test_pretty_date(d, now, expected_str):
    assert pretty_date(d=d, now=now) == expected_str
