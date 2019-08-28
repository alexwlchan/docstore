# -*- encoding: utf-8

import collections

import attr


@attr.s
class SearchOptions:
    tag_query = attr.ib(default=())


def get_tag_aggregation(objects):
    tags = collections.defaultdict(int)
    for obj in objects:
        for t in obj.get("tags", []):
            tags[t] += 1

    return tags
