# -*- encoding: utf-8

import datetime as dt
import json
import pathlib
import urllib.parse

import attr
import humanize
import jinja2
import smartypants

import multilevel_tag_list


TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"


def query_str_only(url):
    if not url.query:
        return "?"
    else:
        return "?" + str(url).split("?")[1]


def since_now_date_str(x):
    result = humanize.naturaltime(
        dt.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f"),
        dt.datetime.now()
    )

    if result == "now":
        return "just now"
    else:
        return result


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


def dump_tag_aggregation(aggregation):
    tags = sorted(aggregation.keys(), key=lambda k: aggregation[k], reverse=True)
    return json.dumps(tags)


def create_env(templates_dir):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader([templates_dir]),
        autoescape=jinja2.select_autoescape(["html"])
    )

    env.filters["since_now_date_str"] = since_now_date_str
    env.filters["short_url"] = lambda u: urllib.parse.urlparse(u).netloc
    env.filters["query_str_only"] = query_str_only
    env.filters["smartypants"] = smartypants.smartypants
    env.filters["render_multilevel_tags"] = multilevel_tag_list.render_tags

    env.filters["static_url"] = lambda filename: "static/" + filename
    env.filters["file_url"] = lambda doc: "files/" + str(doc["file_identifier"])
    env.filters["thumbnail_url"] = lambda doc: "thumbnails/" + str(doc["thumbnail_identifier"])

    env.filters["dump_tag_aggregation"] = dump_tag_aggregation

    env.filters["json"] = lambda s: json.dumps(s)

    return env


ENV = create_env(TEMPLATES_DIR)

TEMPLATE = ENV.get_template("document_list.html")


def render_document_list(
    documents,
    tag_aggregation,
    view_options,
    tag_query,
    title,
    req_url,
    api_version,
    pagination,
    accent_color="#007bff"
):
    idx_start = pagination.page_size * (pagination.current_page - 1)
    idx_end = pagination.page_size * pagination.current_page

    display_documents = documents[idx_start:idx_end]

    return TEMPLATE.render(
        display_documents=display_documents,
        view_options=view_options,
        tag_query=tag_query,
        tag_aggregation=tag_aggregation,
        title=title,
        req_url=req_url,
        accent_color=accent_color,
        pagination=pagination,
        api_version=api_version
    )
