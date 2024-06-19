from collections.abc import Iterator
import datetime
import re
import pathlib
import shutil
import typing

import bs4
from flask.testing import FlaskClient
import pytest

from docstore.documents import store_new_document, write_documents
from docstore.models import Document
from docstore.server import create_app


@pytest.fixture
def client(root: pathlib.Path) -> Iterator[FlaskClient]:
    app = create_app(root=root, title="My test instance", thumbnail_width=200)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_empty_response(client: FlaskClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"no documents found!" in resp.data


def test_shows_documents(
    tmpdir: pathlib.Path, root: pathlib.Path, client: FlaskClient
) -> None:
    for _ in range(3):
        shutil.copyfile("tests/files/cluster.png", str(tmpdir / "cluster.png"))
        store_new_document(
            root=root,
            path=tmpdir / "cluster.png",
            title="My test document",
            tags=["tag1", "tag2", "tag3"],
            source_url="https://example.org/cluster",
            date_saved=datetime.datetime.now(),
        )

    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.data.count(b"My test document") == 3
    assert b"date saved: just now" in resp.data

    # TODO: Detect this thumbnail URL from the page HTML
    resp = client.get("/thumbnails/c/cluster.png")
    assert resp.data[:8] == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"  # PNG magic number

    resp = client.get("/files/c/cluster.png")
    assert resp.data == open("tests/files/cluster.png", "rb").read()


def test_filters_documents_by_tag(root: pathlib.Path, client: FlaskClient) -> None:
    documents = [Document(title=f"Document {i}", tags=[f"tag{i}"]) for i in range(3)]
    write_documents(root=root, documents=documents)

    resp = client.get("/?tag=tag0")
    assert resp.status_code == 200
    assert b"Document 0" in resp.data
    assert b"Document 1" not in resp.data
    assert b"Document 2" not in resp.data


def test_paginates_document(root: pathlib.Path, client: FlaskClient) -> None:
    documents = [Document(title=f"Document {i}") for i in range(200)]
    write_documents(root=root, documents=documents)

    resp = client.get("/")
    assert resp.status_code == 200

    # More recent documents appear first
    assert b"Document 199" in resp.data
    assert b"Document 100" in resp.data
    assert b"Document 99" not in resp.data

    assert "« prev" in resp.data.decode("utf8")
    assert "next »" in resp.data.decode("utf8")

    resp_page_2 = client.get("/?page=2")
    assert resp_page_2.status_code == 200
    assert b"Document 100" not in resp_page_2.data
    assert b"Document 99" in resp_page_2.data
    assert b"Document 0" in resp_page_2.data


def test_documents_with_lots_of_tags(root: pathlib.Path, client: FlaskClient) -> None:
    documents = [Document(title=f"Document {i}", tags=[f"tag{i}"]) for i in range(200)]

    documents.extend(
        [
            Document(title="Another document", tags=["nest0:tag1"]),
            Document(title="Another document", tags=["nest0:tag1:tagA"]),
            Document(title="Another document", tags=["nest0:tag1:tagB"]),
            Document(title="Another document", tags=["nest1:tag1"]),
        ]
    )

    write_documents(root=root, documents=documents)

    resp = client.get("/")
    assert resp.status_code == 200

    assert b'<details id="tagList">' in resp.data


def tidy(html_str: typing.Any) -> str:
    assert isinstance(html_str, str)
    return re.sub(r"\s+", " ", html_str.strip())


class TestCase(typing.TypedDict):
    tags: list[str]
    expected_title: str
    urls: list[str]


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "tags": ["by:John Smith"],
            "expected_title": "{title}, by John Smith ({doc_id})",
            "urls": ["/", "/?tag=by%3AJohn+Smith"],
        },
        {
            "tags": ["by:John Smith", "by:Jane Doe"],
            "expected_title": "{title}, by John Smith, Jane Doe ({doc_id})",
            "urls": [
                "/",
                "/?tag=by%3AJohn+Smith",
                "/?tag=by%3AJane+Doe",
                "/?tag=by%3AJane+Doe&tag=by%3AJohn+Smith",
            ],
        },
        {
            "tags": ["from:ACME Corp"],
            "expected_title": "{title}, from ACME Corp ({doc_id})",
            "urls": ["/", "/?tag=from%3AACME+Corp"],
        },
        {
            "tags": ["from:ACME Corp", "from:Widget Inc"],
            "expected_title": "{title}, from ACME Corp, Widget Inc ({doc_id})",
            "urls": [
                "/",
                "/?tag=from%3AACME+Corp",
                "/?tag=from%3AWidget+Inc",
                "/?tag=from%3AACME+Corp&tag=from%3AWidget+Inc",
            ],
        },
        {
            "tags": ["by:John Smith", "from:ACME Corp"],
            "expected_title": "{title}, by John Smith, from ACME Corp ({doc_id})",
            "urls": [
                "/",
                "/?tag=by%3AJohn+Smith",
                "/?tag=from%3AACME+Corp",
                "/?tag=by%3AJohn+Smith&tag=from%3AACME+Corp",
            ],
        },
    ],
)
def test_shows_attribution_tags(
    root: pathlib.Path, client: FlaskClient, test_case: TestCase
) -> None:
    doc_tags = test_case["tags"] + ["tag1", "tag2"]

    doc = Document(title="My document", tags=doc_tags)
    write_documents(root=root, documents=[doc])

    for url in test_case["urls"]:
        print(url)
        resp = client.get(url)
        assert resp.status_code == 200

        soup = bs4.BeautifulSoup(resp.data, "html.parser")

        h2_title = soup.find("h2", attrs={"class": "title"})
        assert h2_title is not None
        assert tidy(h2_title.text) == test_case["expected_title"].format(
            title=doc.title, doc_id=doc.id
        )

        tags_list = soup.find("div", attrs={"class": "tags"})
        assert tags_list is not None
        assert tidy(tags_list.text) == "tagged with: tag1 tag2"


def test_links_attribution_tags(root: pathlib.Path, client: FlaskClient) -> None:
    doc = Document(title="My document", tags=["by:John Smith"])
    write_documents(root=root, documents=[doc])

    # If the tag is not selected, the attribution tag in the title is a link
    # that filters to the selected tag.
    resp = client.get("/")
    assert resp.status_code == 200

    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    h2_title = soup.find("h2", attrs={"class": "title"})
    assert isinstance(h2_title, bs4.Tag)
    assert h2_title.find("a", attrs={"href": "?tag=by%3AJohn+Smith"}) is not None

    # If the tag is selected, the attribution tag in the title is regular text,
    # not a link.
    resp = client.get("/?tag=by%3aJohn+Smith")
    assert resp.status_code == 200

    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    h2_title = soup.find("h2", attrs={"class": "title"})
    assert h2_title is not None
    assert h2_title.find("a") is None


def test_sets_thumbnail_width(client: FlaskClient) -> None:
    """
    If the user sets a custom thumbnail width, the appropriate CSS style is
    added to the rendered page.
    """
    client.application.config["THUMBNAIL_WIDTH"] = 100

    resp = client.get("/")

    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    style_tag = soup.find("style")
    assert isinstance(style_tag, bs4.Tag)
    assert tidy(style_tag.string) == ".thumbnail { width: 100px; }"


def test_tags_are_sorted_alphabetically(
    root: pathlib.Path, client: FlaskClient
) -> None:
    doc = Document(title="My document", tags=["bulgaria", "austria", "croatia"])
    write_documents(root=root, documents=[doc])

    resp = client.get("/")

    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    tags_div = soup.find("div", attrs={"class": "tags"})
    assert tags_div is not None
    assert tidy(tags_div.text) == "tagged with: austria bulgaria croatia"


def test_gets_curly_quotes(root: pathlib.Path, client: FlaskClient) -> None:
    app = create_app(root=root, title="Isn't this a good title?", thumbnail_width=200)
    app.config["TESTING"] = True

    with app.test_client() as client:
        resp = client.get("/")

    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    title = soup.find("title")
    assert title is not None
    assert title.text.strip() == "docstore/Isn’t this a good title?"

    aside_inner = soup.find("div", attrs={"id": "aside_inner"})
    assert aside_inner is not None
    assert aside_inner.text.strip() == "docstore/Isn’t this a good title?"
