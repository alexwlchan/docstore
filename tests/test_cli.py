import shutil

from click.testing import CliRunner
import pytest

from docstore.cli import main
from docstore.documents import read_documents
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
