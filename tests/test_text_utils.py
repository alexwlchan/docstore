import pytest

from docstore.text_utils import common_prefix, slugify


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
