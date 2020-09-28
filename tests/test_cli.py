import shutil

from click.testing import CliRunner
import pytest

from docstore.cli import main
from docstore.documents import read_documents, write_documents
from docstore.models import Document
from test_models import is_recent


@pytest.fixture
def runner():
    return CliRunner()


class TestAdd:
    def test_stores_new_document(self, tmpdir, root, runner):
        shutil.copyfile(src="tests/files/cluster.png", dst=tmpdir / "My Cluster.png")
        result = runner.invoke(
            main,
            ['add', '--root', str(root), '--path', str(tmpdir / 'My Cluster.png')]
        )

        assert result.exit_code == 0, result.output

        doc_id = result.output.strip()

        documents = read_documents(root)

        assert len(documents) == 1
        assert documents[0].id == doc_id
        assert documents[0].title == ""
        assert documents[0].tags == []
        assert is_recent(documents[0].date_saved)

        assert len(documents[0].files) == 1
        f = documents[0].files[0]
        assert f.filename == "My Cluster.png"
        assert f.path == "files/m/my-cluster.png"
        assert f.source_url is None
        assert f.date_saved == documents[0].date_saved

    @pytest.mark.parametrize('tag_arg, expected_tags', [
        ('', []),
        ('tag with trailing whitespace ', ['tag with trailing whitespace']),
        ('multiple,comma,separated,tags', ['multiple', 'comma', 'separated', 'tags']),
    ])
    def test_adds_tags_to_document(self, tmpdir, root, runner, tag_arg, expected_tags):
        shutil.copyfile(src="tests/files/cluster.png", dst=tmpdir / "My Cluster.png")
        result = runner.invoke(
            main,
            ['add', '--root', str(root), '--path', str(tmpdir / 'My Cluster.png'), '--tags', tag_arg]
        )

        assert result.exit_code == 0, result.output

        documents = read_documents(root)
        assert documents[0].tags == expected_tags

    @pytest.mark.parametrize('source_url_arg, expected_source_url', [
        ('', ''),
        ('https://example.org/cluster.png', 'https://example.org/cluster.png')
    ])
    def test_adds_source_url_to_file(self, tmpdir, root, runner, source_url_arg, expected_source_url):
        shutil.copyfile(src="tests/files/cluster.png", dst=tmpdir / "My Cluster.png")
        result = runner.invoke(
            main,
            ['add', '--root', str(root), '--path', str(tmpdir / 'My Cluster.png'), '--source_url', source_url_arg]
        )

        assert result.exit_code == 0, result.output

        documents = read_documents(root)
        assert documents[0].files[0].source_url == expected_source_url


class TestMerge:
    def test_merges_two_documents_with_identical_metadata(self, root, runner):
        documents = [
            Document(title="My Document", tags=["tag1", "tag2", "tag3"])
            for _ in range(3)
        ]

        write_documents(root=root, documents=documents)

        result = runner.invoke(
            main,
            ["merge", "--yes", "--root", root] + [doc.id for doc in documents]
        )
        assert result.exit_code == 0, result.output

        stored_documents = read_documents(root)

        assert len(stored_documents) == 1
        assert stored_documents[0].id == documents[0].id
        assert stored_documents[0].title == "My Document"
        assert stored_documents[0].tags == ["tag1", "tag2", "tag3"]
