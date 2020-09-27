import datetime
import shutil

import pytest

from docstore.documents import store_new_document, write_documents
from docstore.models import Document
from docstore.server import create_app


@pytest.fixture
def client(root):
    app = create_app(root)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_empty_response(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"No documents found!" in resp.data


def test_shows_documents(tmpdir, root, client):
    for _ in range(3):
        shutil.copyfile("tests/files/cluster.png", str(tmpdir / "cluster.png"))
        store_new_document(
            root=root,
            path=str(tmpdir / "cluster.png"),
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
    assert resp.data[:8] == b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"  # PNG magic number


def test_filters_documents_by_tag(root, client):
    documents = [Document(title=f"Document {i}", tags=[f"tag{i}"]) for i in range(3)]
    write_documents(root=root, documents=documents)

    resp = client.get("/?tag=tag0")
    assert resp.status_code == 200
    assert b"Document 0" in resp.data
    assert b"Document 1" not in resp.data
    assert b"Document 2" not in resp.data


def test_paginates_document(root, client):
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
