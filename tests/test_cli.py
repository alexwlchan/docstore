import datetime
import os
import pathlib
import shutil
import uuid

from click.testing import CliRunner
import pytest

from docstore.cli import main
from docstore.documents import read_documents, store_new_document, write_documents
from docstore.models import Dimensions, Document, File, Thumbnail
from test_models import is_recent


class TestAdd:
    def test_stores_new_document(
        self, tmpdir: pathlib.Path, root: pathlib.Path
    ) -> None:
        shutil.copyfile(src="tests/files/cluster.png", dst=tmpdir / "My Cluster.png")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                f"--root={root}",
                "add",
                str(tmpdir / "My Cluster.png"),
                "--title",
                "My first document",
                "--tags",
                "tag1, tag2, tag3",
            ],
        )

        assert result.exit_code == 0, result.output

        doc_id = result.output.strip()

        documents = read_documents(root)

        assert len(documents) == 1
        assert documents[0].id == doc_id
        assert documents[0].title == "My first document"
        assert documents[0].tags == ["tag1", "tag2", "tag3"]
        assert is_recent(documents[0].date_saved)

        assert len(documents[0].files) == 1
        f = documents[0].files[0]
        assert f.filename == "My Cluster.png"
        assert f.path == "files/m/my-cluster.png"
        assert f.source_url is None
        assert f.date_saved == documents[0].date_saved

    @pytest.mark.parametrize(
        "tag_arg, expected_tags",
        [
            ("", []),
            ("tag with trailing whitespace ", ["tag with trailing whitespace"]),
            (
                "multiple,comma,separated,tags",
                ["multiple", "comma", "separated", "tags"],
            ),
        ],
    )
    def test_adds_tags_to_document(
        self,
        tmpdir: pathlib.Path,
        root: pathlib.Path,
        tag_arg: str,
        expected_tags: list[str],
    ) -> None:
        shutil.copyfile(src="tests/files/cluster.png", dst=tmpdir / "My Cluster.png")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                f"--root={root}",
                "add",
                str(tmpdir / "My Cluster.png"),
                "--title",
                "My second document",
                "--tags",
                tag_arg,
            ],
        )

        assert result.exit_code == 0, result.output

        documents = read_documents(root)
        assert documents[0].tags == expected_tags

    @pytest.mark.parametrize(
        "source_url_arg, expected_source_url",
        [
            ("", ""),
            ("https://example.org/cluster.png", "https://example.org/cluster.png"),
        ],
    )
    def test_adds_source_url_to_file(
        self,
        tmpdir: pathlib.Path,
        root: pathlib.Path,
        source_url_arg: str,
        expected_source_url: str,
    ) -> None:
        shutil.copyfile(src="tests/files/cluster.png", dst=tmpdir / "My Cluster.png")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                f"--root={root}",
                "add",
                str(tmpdir / "My Cluster.png"),
                "--title",
                "My stored document",
                "--tags",
                "tag1, tag2, tag3",
                "--source_url",
                source_url_arg,
            ],
        )

        assert result.exit_code == 0, result.output

        documents = read_documents(root)
        assert documents[0].files[0].source_url == expected_source_url


class TestMerge:
    @pytest.mark.parametrize("doc_count", [1, 2, 3, 4])
    def test_merges_documents_with_identical_metadata(
        self, root: pathlib.Path, doc_count: int
    ) -> None:
        documents = [
            Document(title="My Document", tags=["tag1", "tag2", "tag3"])
            for _ in range(doc_count)
        ]

        write_documents(root=root, documents=documents)

        runner = CliRunner()
        result = runner.invoke(
            main, [f"--root={root}", "merge", "--yes"] + [doc.id for doc in documents]
        )
        assert result.exit_code == 0, result.output

        if doc_count > 1:
            assert "Using common title: My Document\n" in result.output
            assert "Using common tags: tag1, tag2, tag3\n" in result.output

        stored_documents = read_documents(root)

        assert len(stored_documents) == 1
        assert stored_documents[0].id == documents[0].id
        assert stored_documents[0].title == "My Document"
        assert stored_documents[0].tags == ["tag1", "tag2", "tag3"]

    def test_merges_documents_with_inferred_metadata(self, root: pathlib.Path) -> None:
        documents = [
            Document(title=f"My Document {i}", tags=[f"tag{i}"]) for i in range(3)
        ]

        write_documents(root=root, documents=documents)

        runner = CliRunner()
        result = runner.invoke(
            main, [f"--root={root}", "merge", "--yes"] + [doc.id for doc in documents]
        )
        assert result.exit_code == 0, result.output

        assert "Guessed title: My Document\n" in result.output
        assert "Guessed tags: tag0, tag1, tag2\n" in result.output

        stored_documents = read_documents(root)

        assert len(stored_documents) == 1
        assert stored_documents[0].id == documents[0].id
        assert stored_documents[0].title == "My Document"
        assert stored_documents[0].tags == ["tag0", "tag1", "tag2"]

    @pytest.mark.parametrize("doc_count", [1, 2, 3, 4])
    def test_merging_combines_files(self, root: pathlib.Path, doc_count: int) -> None:
        shutil.copyfile(src="tests/files/cluster.png", dst=root / "cluster.png")
        documents = [
            Document(
                title="My Document",
                tags=["tag"],
                files=[
                    File(
                        filename=f"cluster{i}.png",
                        path="cluster.png",
                        size=100,
                        checksum="sha256:123",
                        thumbnail=Thumbnail(
                            path="cluster.png",
                            dimensions=Dimensions(400, 300),
                            tint_color="#000000",
                        ),
                    )
                ],
            )
            for i in range(doc_count)
        ]

        write_documents(root=root, documents=documents)

        runner = CliRunner()
        result = runner.invoke(
            main, [f"--root={root}", "merge", "--yes"] + [doc.id for doc in documents]
        )
        assert result.exit_code == 0, result.output

        stored_documents = read_documents(root)

        assert len(stored_documents) == 1
        assert len(stored_documents[0].files) == doc_count


def test_deleting_document_through_cli(
    tmpdir: pathlib.Path, root: pathlib.Path
) -> None:
    shutil.copyfile(src="tests/files/cluster.png", dst=tmpdir / "cluster.png")

    doc1 = store_new_document(
        root=root,
        path=tmpdir / "cluster.png",
        title="A document about to be deleted",
        tags=[],
        source_url="https://example.org/cluster.png",
        date_saved=datetime.datetime.now(),
    )
    doc2 = Document(title="Doc1", date_saved=datetime.datetime(2010, 1, 1))
    doc3 = Document(title="Doc2", date_saved=datetime.datetime(2002, 2, 2))

    write_documents(root=root, documents=[doc1, doc2, doc3])

    assert read_documents(root) == [doc1, doc2, doc3]

    runner = CliRunner()
    result = runner.invoke(main, [f"--root={root}", "delete", doc1.id, doc2.id])
    assert result.exit_code == 0, result.output

    assert read_documents(root) == [doc3]

    for deleted_doc in [doc1, doc2]:
        deleted_json_path = root / "deleted" / deleted_doc.id / "document.json"
        assert os.path.exists(deleted_json_path)


def test_deleting_in_empty_instance_is_error(root: pathlib.Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, [f"--root={root}", "delete", str(uuid.uuid4())])

    assert result.exit_code == 1, result.output
    assert result.output.strip() == f"There is no docstore instance at {root}!"
