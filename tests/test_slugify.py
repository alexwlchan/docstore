# -*- encoding: utf-8

import pytest

from slugify import slugify


@pytest.mark.parametrize("u, expected_slug", [
    ("abc", "abc"),
    ("a:b", "a-b"),
    ("Çingleton", "cingleton"),
    ("a b", "a-b"),
    ("a_b", "a-b"),
    ("a  b", "a-b"),
])
def test_slugify(u, expected_slug):
    assert slugify(u) == expected_slug
