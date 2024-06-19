"""
Given a series of tags, arrange them into a hierarchy.  For example:
    - seasons
        - autumn
        - summer
    - trees
        - ash
        - oak
        - yew
            - ancient
This is based on
https://github.com/dreamwidth/dw-free/blob/6ec1e146d3c464e506a77913f0abf0d51a944f95/styles/core2.s2#L4126
"""


def render_tag_list(tag_tally):
    if not tag_tally:
        return []

    prev_tags = []
    tag_list_pos = 0
    tier_elements = []
    levels_to_close = 0

    result = []

    for name, count in sorted(tag_tally.items()):
        tags = name.split(":")

        pos = 0
        show_lower_tiers = False

        for tier in tags:
            # If we're on a tag's last tier and this tag isn't already selected,
            # we need to return a link to the tag, otherwise plain text is returned.
            if len(tags) == pos + 1:
                tier_elements = [
                    {
                        "type": "tag_link",
                        "name": name,
                        "count": count,
                        "display_name": tier.lstrip("_"),
                    }
                ]
            else:
                tier_elements = [{"type": "tag_text", "display_name": tier}]

            # Prev tag has fewer tiers than than current tag.
            if len(prev_tags) < pos + 1:
                result.append({"type": "html_literal", "value": "<ul><li>"})
                result.extend(tier_elements)
                levels_to_close += 1

            elif tags[pos] != prev_tags[pos] or show_lower_tiers:
                if tags[pos] != prev_tags[pos]:
                    # The current tag's tier is not the same as the previous
                    # tag's tier of the same level.  This means we may need
                    # to close some lists.
                    i = levels_to_close
                    for html in prev_tags:
                        if i > pos + 1:
                            result.append(
                                {
                                    "type": "html_literal",
                                    "value": "</li></ul>",
                                }
                            )
                            levels_to_close -= 1
                        i -= 1

                    # If we just closed some lists, that means that any lower
                    # tiers in this tag need to be explicitly displayed, even
                    # if they match the same-level tier of the previous tag
                    show_lower_tiers = True

                if levels_to_close <= pos:
                    # This is the first tier at this level, so open list
                    result.append({"type": "html_literal", "value": "<ul><li>"})
                    result.extend(tier_elements)
                    levels_to_close += 1

                else:
                    result.append({"type": "html_literal", "value": "</li><li>"})
                    result.extend(tier_elements)

            else:
                # The current tag's tier is exactly the same as the previous
                # tag's tier at this same level.  It has already been included
                # in the list, so do nothing.
                pass

            # Moving on to next tier in this tag!
            pos += 1

        prev_tags = tags
        show_lower_tiers = False

    # Next tag in the list!
    tag_list_pos += 1

    # All the tags have been added so close all outstanding lists.
    for html in prev_tags:
        if levels_to_close > 0:
            result.append({"type": "html_literal", "value": "</li></ul>"})
            levels_to_close -= 1
        else:  # pragma: no cover
            # I haven't been able to find a test case that triggers this
            # particular branch, so I'm excluding it from coverage.
            # If it does come up, come back and add a test for this line!
            assert 0

    return result
