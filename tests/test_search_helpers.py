# -*- encoding: utf-8

import pytest

from search_helpers import get_tag_aggregation


@pytest.mark.parametrize("objects, expected_aggregation", [
    ([], {}),
    ([{"tags": []}, {"name": "alex"}], {}),
    (
        [{"tags": ["a"]}, {"tags": ["a", "b"]}, {"tags": ["b", "c"]}],
        {"a": 2, "b": 2, "c": 1}
    ),
])
def test_get_tag_aggregation(objects, expected_aggregation):
    assert get_tag_aggregation(objects) == expected_aggregation
