# -*- encoding: utf-8
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

def _query_str_only(url):
    return "?" + str(url).split("?")[1]


def render_tags(req_url, tag_counter):
    if not tag_counter:
        return ""

    def _format_tag(tag):
        return _query_str_only(req_url.add("tag", tag))

    result = ""

    prev_tags = []
    tag_list_pos = 0
    tier_code = ""
    levels_to_close = 0

    for tag_name, count in sorted(tag_counter.items()):
        tags = tag_name.split(":")

        pos = 0
        show_lower_tiers = False

        for tier in tags:
            # If we're on a tag's last tier, we need to return a link to the tag,
            # otherwise plain text is returned.
            if len(tags) == pos + 1:
                tier_code = f'<a href="{_format_tag(tag_name)}">{tier} ({count})</a>'
            else:
                tier_code = f'<span class="non-link-tag">{tier}</span>'

            # Prev tag has fewer tiers than than current tag.
            if len(prev_tags) < pos + 1:
                result += f'\n<ul><li>{tier_code}'
                levels_to_close += 1

            elif tags[pos] != prev_tags[pos] or show_lower_tiers:
                if tags[pos] != prev_tags[pos]:

                    # The current tag's tier is not the same as the previous
                    # tag's tier of the same level.  This means we may need
                    # to close some lists.
                    i = levels_to_close
                    for html in prev_tags:
                        if i > pos + 1:
                            result += "</li></ul>"
                            levels_to_close -= 1
                        i -= 1

                    # If we just closed some lists, that means that any lower
                    # tiers in this tag need to be explicitly displayed, even
                    # if they match the same-level tier of the previous tag
                    show_lower_tiers = True

                if levels_to_close <= pos:
                    # This is the first tier at this level, so open list
                    result += f"\n<ul><li>{tier_code}"
                    levels_to_close += 1

                else:
                    # There have already been tiers added at this level
                    result += f"</li>\n<li>{tier_code}"

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
            result += "</li></ul>"
            levels_to_close -= 1

    return result
