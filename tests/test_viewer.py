# -*- encoding: utf-8

import datetime as dt
import re

import bs4
import hyperlink
import pytest

from pagination import Pagination
import viewer


def get_html(
    documents=[],
    tag_aggregation={},
    view_options=viewer.ViewOptions(),
    tag_query=[],
    req_url=hyperlink.URL.from_text("http://localhost:9000/request"),
    title="docstore test instance",
    pagination=Pagination(
        page_size=25,
        current_page=1,
        total_documents=100
    ),
    api_version="test_1.0.0"
):
    return viewer.render_document_list(
        documents=documents,
        tag_aggregation=tag_aggregation,
        view_options=view_options,
        tag_query=tag_query,
        req_url=req_url,
        title=title,
        pagination=pagination,
        api_version=api_version
    )


def get_html_soup(**kwargs):
    html = get_html(**kwargs)

    return bs4.BeautifulSoup(html, "html.parser")


def test_empty_state():
    html = get_html(documents=[])

    assert "No documents found" in html


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

    @pytest.mark.parametrize("list_view", [None, 1, "circles", "cloud"])
    def test_only_allows_certain_list_view(self, list_view):
        with pytest.raises(ValueError):
            viewer.ViewOptions(list_view=list_view)

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

    @pytest.mark.parametrize("tag_view", [None, 1, "circles", "table"])
    def test_only_allows_certain_tag_view(self, tag_view):
        with pytest.raises(ValueError):
            viewer.ViewOptions(tag_view=tag_view)


class TestUserMessages:

    def test_no_message(self):
        html_soup = get_html_soup(
            req_url=hyperlink.URL.from_text("http://localhost:1234")
        )

        assert html_soup.find("alert") is None

    def test_success_message(self):
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


def test_all_urls_are_relative(document):
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
    def test_displays_tags_in_form(self):
        html_soup = get_html_soup(
            tag_query=["x", "y", "z"]
        )
        tag_field = html_soup.find("input", attrs={"name": "tags"})
        assert tag_field.attrs["value"] == "x y z"

    def test_url_decodes_tags_before_displaying(self, document):
        """
        Check that URL-encoded entities get unwrapped when we display the tag form.

        e.g. "colour:blue" isn't displayed as "colour%3Ablue"

        """
        document["tags"] = ["colour:blue"]

        html_soup = get_html_soup(
            documents=[document],
            tag_query=["colour:blue"]
        )
        tag_field = html_soup.find("input", attrs={"name": "tags"})
        assert tag_field.attrs["value"] == "colour:blue"


@pytest.mark.parametrize("list_view", ["table", "grid"])
def test_includes_source_url(document, list_view):
    source_url = "https://example.org/document.pdf"
    document["user_data"] = {"source_url": source_url}

    html = get_html(
        documents=[document],
        view_options=viewer.ViewOptions(list_view=list_view)
    )

    assert f'<a href="{source_url}">example.org</a>' in html


def test_omits_source_url_if_empty(document):
    document["user_data"] = {"source_url": ""}

    html_soup = get_html_soup(documents=[document])
    assert len(html_soup.find_all("section")) == 1
    assert html_soup.find("div", attrs={"id": "document__metadata__source_url"}) is None


def test_renders_titles_with_pretty_quotes(document):
    document["title"] = "Isn't it a wonderful day? -- an optimist"

    html_soup = get_html_soup(documents=[document])
    title = html_soup.find("div", attrs={"class": "document__title"})
    assert "Isn’t it a wonderful day? — an optimist" in title.text


class TestNavbarOptions:
    @staticmethod
    def get_sort_options(html_soup):
        dropdown = html_soup.find("li", attrs={"id": "navbarSortBy"})

        items = dropdown.find("div", attrs={"class": "dropdown-menu"}).find_all("a")

        return {
            it.text: it.attrs["href"] for it in items
        }

    @staticmethod
    def get_view_options(html_soup):
        dropdown = html_soup.find("li", attrs={"id": "navbarViewAs"})

        items = dropdown.find("div", attrs={"class": "dropdown-menu"}).find_all("a")

        return {
            it.text: it.attrs["href"] for it in items
        }

    @staticmethod
    def assert_query_param_equal(query1, query2):
        assert (
            sorted(hyperlink.URL.from_text(query1).query) ==
            sorted(hyperlink.URL.from_text(query2).query)
        )

    @pytest.mark.parametrize("req_url", [
        "http://localhost:1234",
        "http://localhost:1234?sort=title:a_z",
    ])
    def test_sets_sort_option(self, req_url):
        html_soup = get_html_soup(
            req_url=hyperlink.URL.from_text(req_url)
        )

        assert self.get_sort_options(html_soup) == {
            "title (a-z)": "?sort=title:a_z",
            "title (z-a)": "?sort=title:z_a",
            "date created (newest first)": "?sort=date_created:newest_first",
            "date created (oldest first)": "?sort=date_created:oldest_first",
        }

    def test_preserves_other_query_params_setting_sort_option(self):
        html_soup = get_html_soup(
            req_url=hyperlink.URL.from_text(
                "http://localhost:1234?tag=x&tag=y"
            )
        )

        expected = {
            "title (a-z)": "?tag=x&tag=y&sort=title:a_z",
            "title (z-a)": "?tag=x&tag=y&sort=title:z_a",
            "date created (newest first)": "?tag=x&tag=y&sort=date_created:newest_first",
            "date created (oldest first)": "?tag=x&tag=y&sort=date_created:oldest_first",
        }

        for label, url in self.get_sort_options(html_soup).items():
            self.assert_query_param_equal(url, expected[label])

    @pytest.mark.parametrize("req_url", [
        "http://localhost:1234",
        "http://localhost:1234?view=table",
    ])
    def test_sets_view_option(self, req_url):
        html_soup = get_html_soup(
            req_url=hyperlink.URL.from_text(req_url)
        )

        assert self.get_view_options(html_soup) == {
            "table": "?view=table",
            "grid": "?view=grid",
        }

    def test_preserves_other_query_params_setting_view_option(self):
        html_soup = get_html_soup(
            req_url=hyperlink.URL.from_text(
                "http://localhost:1234?tag=x&tag=y"
            )
        )

        expected = {
            "table": "?tag=x&tag=y&view=table",
            "grid": "?tag=x&tag=y&view=grid",
        }

        for label, url in self.get_view_options(html_soup).items():
            self.assert_query_param_equal(url, expected[label])


def test_uses_title_in_head():
    title = "my docstore instance"
    html_soup = get_html_soup(title=title)

    assert html_soup.find("title").text.strip() == title


def test_includes_tags_in_title_if_present():
    title = "my docstore instance"
    html_soup = get_html_soup(
        title=title,
        tag_query=["x", "y", "z"]
    )

    assert html_soup.find("title").text.strip() == f"Tagged with x, y, z — {title}"


def test_selected_tags_are_not_clickable_in_tag_cloud(document):
    document["tags"] = ["a", "b", "c", "d"]

    html_soup = get_html_soup(
        documents=[document],
        tag_query=["a", "b"],
        view_options=viewer.ViewOptions(tag_view="cloud"),
        tag_aggregation={"a": 1, "b": 1, "c": 1, "d": 1}
    )

    tag_cloud = html_soup.find("div", attrs={"id": "collapseTagList"})
    tag_is_link = {
        span_tag.text.strip(): span_tag.find("a") is not None
        for span_tag in tag_cloud.find_all("span", attrs={"class": "tag"})
    }

    assert tag_is_link == {
        "a": False,
        "b": False,
        "c": True,
        "d": True,
    }


def test_includes_list_of_filtered_tags():
    html_soup = get_html_soup(
        req_url=hyperlink.URL.from_text("http://localhost:1234/?tag=alfa&tag=bravo"),
        tag_query=["alfa", "bravo"]
    )

    alert_div = html_soup.find("div", attrs={"class": ["alert", "tag_query"]})
    actual_text = re.sub(r"\s+", " ", alert_div.text.strip())

    expected_text = "Filtering to documents tagged with alfa x bravo x"

    assert actual_text == expected_text

    links = {
        a_tag.attrs["id"].split(":")[1]: a_tag.attrs["href"]
        for a_tag in alert_div.find_all("a")
    }

    assert links == {
        "alfa": "?tag=bravo",
        "bravo": "?tag=alfa",
    }


def test_displays_list_of_tags_on_document(document):
    document["tags"] = ["alfa", "bravo", "charlie"]

    html_soup = get_html_soup(
        documents=[document],
        tag_query=["alfa", "bravo"],
        req_url=hyperlink.URL.from_text("http://localhost:1234/?tag=alfa&tag=bravo")
    )

    tag_info = html_soup.find("div", attrs={"class": "document__metadata__tags"})

    tag_names = [
        span_tag.text.strip()
        for span_tag in tag_info.find_all("span")
    ]

    assert tag_names == ["#alfa", "#bravo", "#charlie"]

    tag_is_link = {
        span_tag.text.strip(): span_tag.find("a") is not None
        for span_tag in tag_info.find_all("span")
    }

    assert tag_is_link == {"#alfa": False, "#bravo": False, "#charlie": True}

    tag_links = [
        a_tag.attrs["href"]
        for a_tag in tag_info.find_all("a")
    ]

    assert tag_links == ["?tag=alfa&tag=bravo&tag=charlie"]


class TestPagination:
    def test_omits_pagination_if_single_page(self):
        html_soup = get_html_soup(
            pagination=Pagination(
                page_size=25,
                current_page=1,
                total_documents=10
            )
        )

        assert html_soup.find("nav", attrs={"id": "pagination"}) is None

    @pytest.mark.parametrize("current_page, expected_classes", [
        (1, ["page-item", "disabled"]),
        (2, ["page-item"]),
    ])
    def test_classes_on_prev_page_button(self, current_page, expected_classes):
        html_soup = get_html_soup(
            pagination=Pagination(
                page_size=25,
                current_page=current_page,
                total_documents=50
            )
        )

        pagination_div = html_soup.find("nav", attrs={"id": "pagination"})
        prev_li = pagination_div.find("li", attrs={"id": "pagination__prev"})
        assert prev_li.attrs["class"] == expected_classes

    @pytest.mark.parametrize("req_url, expected_url", [
        ("http://localhost:1234?page=2", "?"),
        ("http://localhost:1234?tag=alfa&page=2", "?tag=alfa"),
    ])
    def test_prev_page_link_on_page_1(self, req_url, expected_url):
        html_soup = get_html_soup(
            pagination=Pagination(
                page_size=25,
                current_page=2,
                total_documents=50
            ),
            req_url=hyperlink.URL.from_text(req_url)
        )

        pagination_div = html_soup.find("nav", attrs={"id": "pagination"})
        prev_li = pagination_div.find("li", attrs={"id": "pagination__prev"})
        assert prev_li.find("a").attrs["href"] == expected_url

    @pytest.mark.parametrize("req_url, expected_url", [
        ("http://localhost:1234?page=4", "?page=3"),
        ("http://localhost:1234?tag=alfa&page=4", "?tag=alfa&page=3"),
    ])
    def test_prev_page_link_on_later_pages(self, req_url, expected_url):
        html_soup = get_html_soup(
            pagination=Pagination(
                page_size=25,
                current_page=4,
                total_documents=100
            ),
            req_url=hyperlink.URL.from_text(req_url)
        )

        pagination_div = html_soup.find("nav", attrs={"id": "pagination"})
        prev_li = pagination_div.find("li", attrs={"id": "pagination__prev"})
        assert prev_li.find("a").attrs["href"] == expected_url

    def test_creates_page_links_for_each_page(self):
        html_soup = get_html_soup(
            pagination=Pagination(
                page_size=10,
                current_page=2,
                total_documents=50
            )
        )
        pagination_div = html_soup.find("nav", attrs={"id": "pagination"})
        page_links = pagination_div.find_all(
            "a", attrs={"class": "numbered-page-link"})

        actual_links = {
            a_tag.text: a_tag.attrs["href"]
            for a_tag in page_links
        }

        assert actual_links == {
            "1": "?",
            "2": "?page=2",
            "3": "?page=3",
            "4": "?page=4",
            "5": "?page=5",
        }

    @pytest.mark.parametrize("current_page", [1, 2, 3, 4, 5])
    def test_disables_current_page_link(self, current_page):
        html_soup = get_html_soup(
            pagination=Pagination(
                page_size=10,
                current_page=current_page,
                total_documents=50
            )
        )
        pagination_div = html_soup.find("nav", attrs={"id": "pagination"})
        page_links = pagination_div.find_all("li", attrs={"class": "page-item"})

        current_page_link = [
            li_tag
            for li_tag in page_links
            if li_tag.find("a").text == str(current_page)
        ][0]

        assert "disabled" in current_page_link.attrs["class"]

    @pytest.mark.parametrize("current_page, expected_classes", [
        (1, ["page-item"]),
        (2, ["page-item", "disabled"]),
    ])
    def test_classes_on_next_page_button(self, current_page, expected_classes):
        html_soup = get_html_soup(
            pagination=Pagination(
                page_size=25,
                current_page=current_page,
                total_documents=50
            )
        )

        pagination_div = html_soup.find("nav", attrs={"id": "pagination"})
        next_li = pagination_div.find("li", attrs={"id": "pagination__next"})
        assert next_li.attrs["class"] == expected_classes

    @pytest.mark.parametrize("req_url, expected_url", [
        ("http://localhost:1234?page=4", "?page=5"),
        ("http://localhost:1234?tag=alfa&page=4", "?tag=alfa&page=5"),
    ])
    def test_next_page_link(self, req_url, expected_url):
        html_soup = get_html_soup(
            pagination=Pagination(
                page_size=25,
                current_page=4,
                total_documents=200
            ),
            req_url=hyperlink.URL.from_text(req_url)
        )

        pagination_div = html_soup.find("nav", attrs={"id": "pagination"})
        next_li = pagination_div.find("li", attrs={"id": "pagination__next"})
        assert next_li.find("a").attrs["href"] == expected_url

    def test_only_shows_relevant_documents(self):
        documents = [
            {
                "title": f"document {i}",
                "file_identifier": f"{i}/{i}.pdf",
                "date_created": dt.datetime.now().isoformat()
            }
            for i in range(1, 20)
        ]

        html_soup = get_html_soup(
            documents=documents,
            pagination=Pagination(
                page_size=5,
                current_page=2,
                total_documents=len(documents)
            )
        )

        titles = [
            div.text.strip()
            for div in html_soup.find_all("div", attrs={"class": "document__title"})
        ]

        assert titles == [f"document {i}" for i in range(6, 11)]
