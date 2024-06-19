from docstore.tag_list import render_tag_list


def test_empty_render_tag_list() -> None:
    assert render_tag_list({}) == []
