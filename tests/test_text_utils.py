from datetime import datetime

import pytest

from docstore.text_utils import common_prefix, hostname, pretty_date, slugify


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
def test_common_prefix(values: list[str], expected_prefix: str) -> None:
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
def test_slugify(u: str, expected_slug: str) -> None:
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
        (datetime(2001, 1, 1, 13, 0, 0), datetime(2001, 1, 3, 12, 0, 0), "2 days ago"),
    ],
)
def test_pretty_date(d: datetime, now: datetime, expected_str: str) -> None:
    assert pretty_date(d=d, now=now) == expected_str


@pytest.mark.parametrize(
    "url, expected_hostname",
    [
        ("https://example.org/path/to/file.pdf", "example.org"),
        # This really appeared in the source_url of a docstore instance migrated
        # from v1, and caused a 500 error in the app.  It's weird, but shouldn't cause
        # the app to crash.
        ("magic", "magic"),
    ],
)
def test_hostname(url: str, expected_hostname: str) -> None:
    assert hostname(url) == expected_hostname
