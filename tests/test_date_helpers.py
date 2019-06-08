# -*- encoding: utf-8

import datetime as dt

import pytest

from date_helpers import relative_date_str


NOW = dt.datetime.now()


@pytest.mark.parametrize('x, y, expected_relative_str', [
    (NOW, NOW, "just now"),
    (NOW, NOW - dt.timedelta(seconds=90), "1 minute ago"),
    (NOW, NOW - dt.timedelta(seconds=180), "3 minutes ago"),
    (NOW, NOW - dt.timedelta(seconds=60 * 60 * 1.1), "1 hour ago"),
    (NOW, NOW - dt.timedelta(seconds=60 * 60 * 3), "3 hours ago"),
    (NOW, NOW - dt.timedelta(seconds=60 * 60 * 3 + 15 * 60), "3 hours ago"),
    (NOW, NOW - dt.timedelta(seconds=60 * 60 * 24 + 1), "1 day ago"),
    (NOW, NOW - dt.timedelta(seconds=60 * 60 * 24 * 3 + 1), "3 days ago"),
    (NOW, NOW + dt.timedelta(seconds=60 * 60 * 24 * 10 + 1), NOW.strftime("%-d %b %Y")),
    (dt.datetime(2000, 2, 3), NOW, "3 Feb 2000"),
    (dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 30), "1 Jan 2000"),
])
def test_relative_date_str(x, y, expected_relative_str):
    assert relative_date_str(x, y) == expected_relative_str
