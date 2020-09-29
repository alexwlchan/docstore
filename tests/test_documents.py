import datetime
import os
import shutil

from docstore.documents import (
    pairwise_merge_documents,
    read_documents,
    sha256,
    store_new_document,
    write_documents,
)
from docstore.models import Document, File, Thumbnail


def create_file(filename):
    return File(
        filename=filename,
        path=f"files/{filename}",
        size=1,
        checksum="md5:123",
        thumbnail=Thumbnail(f"thumbnails/{filename}.png"),
    )


def test_sha256():
    assert (
        sha256("tests/files/cluster.png")
        == "sha256:683cbee0c2dda22b42fd92bda0f31e4b6b49cd8650a7924d72a14a30f11bfbe5"
    )


def test_read_blank_documents_is_empty(tmpdir):
    assert read_documents(tmpdir) == []


def test_can_write_and_read_documents(tmpdir):
    documents = [Document(title="My first document")]

    write_documents(root=tmpdir, documents=documents)

    # Repeat a couple of times so we hit the caching paths.
    for _ in range(3):
        assert read_documents(tmpdir) == documents


def test_can_merge_documents(root):
    os.makedirs(root / "files")
    shutil.copyfile(src="tests/files/cluster.png", dst=root / "files" / "cluster1.png")
    shutil.copyfile(src="tests/files/cluster.png", dst=root / "files" / "cluster2.png")

    f1 = create_file("cluster1.png")
    f2 = create_file("cluster2.png")

    doc1 = Document(title="My first document", files=[f1], tags=["tag1"])
    doc2 = Document(title="My second document", files=[f2], tags=["tag2"])

    write_documents(root=root, documents=[doc1, doc2])

    pairwise_merge_documents(
        root=root,
        doc1=doc1,
        doc2=doc2,
        new_title="My merged document",
        new_tags=["tag1", "tag2", "new_merged_tag"],
    )

    stored_documents = read_documents(root)

    assert stored_documents == [
        Document(
            id=doc1.id,
            date_saved=doc1.date_saved,
            files=[f1, f2],
            title="My merged document",
            tags=["tag1", "tag2", "new_merged_tag"],
        )
    ]


def test_merging_uses_earliest_date(tmpdir):
    doc1 = Document(title="Doc1", date_saved=datetime.datetime(2010, 1, 1))
    doc2 = Document(title="Doc2", date_saved=datetime.datetime(2002, 2, 2))

    write_documents(root=tmpdir, documents=[doc1, doc2])

    pairwise_merge_documents(
        root=tmpdir,
        doc1=doc1,
        doc2=doc2,
        new_title="DocMerged",
        new_tags=[],
    )

    stored_documents = read_documents(tmpdir)

    assert doc2.date_saved < doc1.date_saved
    assert len(stored_documents) == 1
    assert stored_documents[0].date_saved == doc2.date_saved


def test_store_new_document(tmpdir):
    root = tmpdir / "root"
    shutil.copyfile(src="tests/files/cluster.png", dst=tmpdir / "My Cluster.png")

    documents = read_documents(root)
    assert len(documents) == 0

    now = datetime.datetime(2020, 2, 20)

    new_document = store_new_document(
        root=root,
        path=tmpdir / "My Cluster.png",
        title="My cluster title",
        tags=["tag1", "tag2", "tag3"],
        source_url="https://example.org/cluster.png",
        date_saved=now,
    )

    assert isinstance(new_document, Document)
    assert new_document.title == "My cluster title"
    assert new_document.date_saved == now
    assert new_document.tags == ["tag1", "tag2", "tag3"]

    assert len(new_document.files) == 1
    new_file = new_document.files[0]
    assert isinstance(new_file, File)
    assert new_file.filename == "My Cluster.png"
    assert new_file.path == "files/m/my-cluster.png"
    assert new_file.size == 41151
    assert (
        new_file.checksum
        == "sha256:683cbee0c2dda22b42fd92bda0f31e4b6b49cd8650a7924d72a14a30f11bfbe5"
    )
    assert new_file.source_url == "https://example.org/cluster.png"
    assert new_file.date_saved == now

    assert new_file.thumbnail == Thumbnail("thumbnails/m/my-cluster.png")
    assert os.path.exists(root / new_file.thumbnail.path)

    assert read_documents(root) == [new_document]

    # Storing a second document gets us both documents, but with different names
    shutil.copyfile(src="tests/files/cluster.png", dst=tmpdir / "My Cluster.png")
    new_document2 = store_new_document(
        root=root,
        path=tmpdir / "My Cluster.png",
        title="My second cluster title",
        tags=["tag1", "tag2", "tag3", "tag4"],
        source_url="https://example.org/cluster2.png",
        date_saved=now,
    )

    assert isinstance(new_document2, Document)
    new_file2 = new_document2.files[0]
    assert new_file2.filename == "My Cluster.png"
    assert new_file2.path != "files/m/my-cluster.png"
    assert new_file2.path.startswith("files/m/my-cluster_")
    assert new_file2.path.endswith(".png")

    assert read_documents(root) == [new_document, new_document2]

    assert len(os.listdir(root / "files" / "m")) == 2
    assert len(os.listdir(root / "thumbnails" / "m")) == 2
