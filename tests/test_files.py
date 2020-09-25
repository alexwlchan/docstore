import datetime

from docstore.files import pairwise_merge_documents, read_documents, sha256, write_documents
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


def test_can_merge_documents(tmpdir):
    f1 = create_file("cat1.jpg")
    f2 = create_file("cat2.jpg")

    doc1 = Document(title="My first document", files=[f1], tags=["tag1"])
    doc2 = Document(title="My second document", files=[f2], tags=["tag2"])

    write_documents(root=tmpdir, documents=[doc1, doc2])

    pairwise_merge_documents(
        root=tmpdir,
        doc1=doc1,
        doc2=doc2,
        new_title="My merged document",
        new_tags=["tag1", "tag2", "new_merged_tag"],
    )

    stored_documents = read_documents(tmpdir)

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
        root=tmpdir, doc1=doc1, doc2=doc2, new_title="DocMerged", new_tags=[],
    )

    stored_documents = read_documents(tmpdir)

    assert doc2.date_saved < doc1.date_saved
    assert len(stored_documents) == 1
    assert stored_documents[0].date_saved == doc2.date_saved
