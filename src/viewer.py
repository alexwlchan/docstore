# -*- encoding: utf-8

import pathlib
import urllib.parse

import attr
import jinja2
import smartypants

import date_helpers
import multilevel_tag_list


TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"


def query_str_only(url):
    if not url.query:
        return "?"
    else:
        return "?" + str(url).split("?")[1]


@attr.s(frozen=True)
class ViewOptions:
    list_view = attr.ib(default="table")
    tag_view = attr.ib(default="list")
    expand_document_form = attr.ib(default=False)
    expand_tag_list = attr.ib(default=False)

    @list_view.validator
    def check_list_view(self, attribute, value):
        allowed_values = {"table", "grid"}
        if value not in allowed_values:
            raise ValueError(f"Unrecognised value for list_view: {value}")

    @tag_view.validator
    def check_tag_view(self, attribute, value):
        allowed_values = {"cloud", "list"}
        if value not in allowed_values:
            raise ValueError(f"Unrecognised value for tag_view: {value}")


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


def render_document_list(
    documents,
    tag_aggregation,
    view_options,
    search_options,
    title,
    req_url,
    api_version,
    accent_color="#007bff"
):
    return TEMPLATE.render(
        display_documents=documents,
        view_options=view_options,
        tag_query=search_options.tag_query,
        tag_aggregation=tag_aggregation,
        title=title,
        req_url=req_url,
        accent_color=accent_color,
        api_version=api_version
    )
