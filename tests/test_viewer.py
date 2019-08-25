# -*- encoding: utf-8

import datetime as dt
import re
import time

import bs4
import hyperlink
import pytest

from search_helpers import SearchOptions
import viewer


PARAMS = [
    [("view", "table"), ("tag", "x")],
    [("sort", "title:asc")],
    [("sort", "title:desc")],
    [("sort", "date_created:asc")],
    [("sort", "date_created:desc")],
]


def get_html(
    documents=[],
    tag_aggregation={},
    view_options=viewer.ViewOptions(),
    search_options=SearchOptions(),
    req_url=hyperlink.URL.from_text("http://localhost:9000/request"),
    title="docstore test instance",
    api_version="test_1.0.0"
):
    return viewer.render_document_list(
        documents=documents,
        tag_aggregation=tag_aggregation,
        view_options=view_options,
        search_options=search_options,
        req_url=req_url,
        title=title,
        api_version=api_version
    )


def get_html_soup(**kwargs):
    html = get_html(**kwargs)

    return bs4.BeautifulSoup(html, "html.parser")


# @pytest.fixture
# def sess(api):
#     def raise_for_status(resp, *args, **kwargs):
#         resp.raise_for_status()
#         assert resp.text != "null"
#
#     api.requests.hooks["response"].append(raise_for_status)
#     return api.requests


def test_empty_state():
    html = get_html(documents=[])

    assert "No documents found" in html
    assert '<div class="row">' not in html
    assert '<table class="table">' not in html


class TestViewOptions:

    @staticmethod
    def _assert_is_table(html):
        assert '<main class="documents documents__view_grid">' not in html
        assert '<main class="documents documents__view_table">' in html

    @staticmethod
    def _assert_is_grid(html):
        assert '<main class="documents documents__view_grid">' in html
        assert '<main class="documents documents__view_table">' not in html

    def test_table_view(self, document):
        html = get_html(
            documents=[document],
            view_options=viewer.ViewOptions(list_view="table")
        )

        self._assert_is_table(html)

    def test_grid_view(self, document):
        html = get_html(
            documents=[document],
            view_options=viewer.ViewOptions(list_view="grid")
        )

        self._assert_is_grid(html)

    def test_default_is_table_view(self, document):
        html = get_html(
            documents=[document],
            view_options=viewer.ViewOptions()
        )

        self._assert_is_table(html)

    def test_tag_list_view(self, document):
        html_soup = get_html_soup(
            documents=[document],
            tag_aggregation={"x": 5, "y": 3},
            view_options=viewer.ViewOptions(tag_view="list")
        )

        tag_div = html_soup.find("div", attrs={"id": "collapseTagList"})
        assert tag_div.find("ul") is not None
        assert html_soup.find("div", attrs={"id": "tag_cloud"}) is None

    def test_tag_cloud_view(self, document):
        html_soup = get_html_soup(
            documents=[document],
            tag_aggregation={"x": 5, "y": 3},
            view_options=viewer.ViewOptions(tag_view="cloud")
        )

        tag_div = html_soup.find("div", attrs={"id": "collapseTagList"})
        assert tag_div.find("ul") is None
        assert html_soup.find("div", attrs={"id": "tag_cloud"}) is not None

    def test_tag_view_default_is_list(self, document):
        html_soup = get_html_soup(
            documents=[document],
            tag_aggregation={"x": 5, "y": 3},
            view_options=viewer.ViewOptions(tag_view="list")
        )

        tag_div = html_soup.find("div", attrs={"id": "collapseTagList"})
        assert tag_div.find("ul") is not None
        assert html_soup.find("div", attrs={"id": "tag_cloud"}) is None


class TestUserMessages:

    def test_no_message(self):
        html_soup = get_html_soup(
            req_url=hyperlink.URL.from_text("http://localhost:1234")
        )

        assert html_soup.find("alert") is None

    def test_no_message(self):
        html_soup = get_html_soup(
            req_url=hyperlink.URL.from_text("http://localhost:1234?_message.id=1234")
        )

        success_div = html_soup.find("div", attrs={"class": "alert-success"})
        assert success_div.text.strip().startswith("Stored new document as 1234!")

    def test_error_message(self):
        html_soup = get_html_soup(
            req_url=hyperlink.URL.from_text("http://localhost:1234?_message.error=BOOM")
        )

        danger_div = html_soup.find("div", attrs={"class": "alert-danger"})
        assert danger_div.text.strip().startswith("Unable to store document: BOOM")


def test_renders_title():
    title = "my great docstore"
    html_soup = get_html_soup(title=title)

    header = html_soup.find("a", attrs={"class": "navbar-brand"})
    assert header.text == title


# TODO: Pass proper params here
@pytest.mark.parametrize("params", PARAMS)
def test_all_urls_are_relative(document, params):
    document["tags"] = ["x", "y"]

    html_soup = get_html_soup(documents=[document])
    links = [a.attrs["href"] for a in html_soup.find("main").find_all("a")]

    for href in links:
        assert href.startswith(("?", "#", "files/")), href


def test_version_is_shown_in_footer():
    html_soup = get_html_soup(api_version="1.2.3")
    footer = html_soup.find("footer")
    assert re.search(r'docstore v1\.2\.3', str(footer)) is not None


def test_includes_created_date(document):
    document["created_date"] = dt.datetime.now().isoformat()

    html_soup = get_html_soup(documents=[document])
    date_created_div = html_soup.find(
        "div", attrs={"class": "document__metadata__date_created"})
    assert date_created_div.find(
        "h5", attrs={"class": "document__metadata__info"}).text == "just now"


class TestStoreDocumentForm:
    def test_url_decodes_tags_before_displaying(self, document):
        """
        Check that URL-encoded entities get unwrapped when we display the tag form.

        e.g. "colour:blue" isn't displayed as "colour%3Ablue"

        """
        document["tags"] = ["colour:blue"]

        html_soup = get_html_soup(
            documents=[document],
            search_options=SearchOptions(tag_query=["colour:blue"])
        )
        tag_field = html_soup.find("input", attrs={"name": "tags"})
        assert tag_field.attrs["value"] == "colour:blue"


def test_omits_source_url_if_empty(document):
    document["source_url"] = ""

    html_soup = get_html_soup(documents=[document])
    assert len(html_soup.find_all("section")) == 1
    assert html_soup.find("div", attrs={"id": "document__metadata__source_url"}) is None


def test_renders_titles_with_pretty_quotes(document):
    document["title"] = "Isn't it a wonderful day? -- an optimist"

    html_soup = get_html_soup(documents=[document])
    title = html_soup.find("div", attrs={"class": "document__title"})
    assert "Isn’t it a wonderful day? — an optimist" in title.text
