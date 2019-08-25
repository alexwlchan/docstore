# -*- encoding: utf-8

import pathlib
import urllib.parse

import attr
import hyperlink
import jinja2
import smartypants

import date_helpers
import multilevel_tag_list
import search_helpers


TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"


def query_str_only(url):
    if not url.query:
        return "?"
    else:
        return "?" + str(url).split("?")[1]


@attr.s(frozen=True)
class ViewOptions:
    list_view = attr.ib(default="table")
    tag_filter = attr.ib(default=[])

    @list_view.validator
    def check(self, attribute, value):
        allowed_values = {"table", "grid"}
        if value not in allowed_values:
            raise ValueError(f"Unrecognised value for list_view: {value}")


def create_env(templates_dir):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader([templates_dir]),
        autoescape=jinja2.select_autoescape(["html"])
    )

    env.filters["since_now_date_str"] = date_helpers.since_now_date_str
    env.filters["short_url"] = lambda u: urllib.parse.urlparse(u).netloc
    env.filters["query_str_only"] = query_str_only
    env.filters["smartypants"] = smartypants.smartypants
    env.filters["render_multilevel_tags"] = multilevel_tag_list.render_tags

    env.filters["static_url"] = lambda filename: "static/" + filename
    env.filters["file_url"] = lambda doc: "files/" + str(doc["file_identifier"])
    env.filters["thumbnail_url"] = lambda doc: "thumbnails/" + str(doc["thumbnail_identifier"])

    return env


ENV = create_env(TEMPLATES_DIR)

TEMPLATE = ENV.get_template("document_list.html")


def render_document_list(documents, view_options, api_version):
    print(view_options.tag_filter)
    return TEMPLATE.render(
        display_documents=documents,
        search_options=search_helpers.SearchOptions(
            tag_query=view_options.tag_filter,
            sort_order=("date_created", "desc")
        ),
        tag_aggregation={},
        view_option=view_options.list_view,
        title="whatever",
        req_url=hyperlink.URL.from_text("http://localhost:9000/request"),
        params={},
        cookies={},
        tag_view="cloud",
        accent_color="#ff0000",
        api_version=api_version
    )
