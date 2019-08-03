# -*- encoding: utf-8

import json
import re

from click.testing import CliRunner
import pytest

import api


@pytest.fixture
def runner(monkeypatch):
    def mock_create_api(*create_args, **create_kwargs):
        print("create_args=%r, create_kwargs=%r" % (create_args, create_kwargs))

        class Api:
            def run(self, *run_args, **run_kwargs):
                print("Called run()")
                print("run_args=%r, run_kwargs=%r" % (run_args, run_kwargs))
                pass

        return Api()

    with monkeypatch.context() as m:
        m.setattr(api, "create_api", mock_create_api)
        yield CliRunner()


def test_api_needs_root(runner):
    result = runner.invoke(api.run_api)
    assert result.exit_code == 2
    assert 'Missing argument "ROOT"' in result.output


def test_api_starts(runner, store_root):
    result = runner.invoke(api.run_api, [str(store_root)])

    assert result.exit_code == 0
    assert "Called run()" in result.output
    assert str(store_root) in result.output


def test_api_sets_title(runner, store_root):
    result = runner.invoke(api.run_api, [str(store_root), "--title", "manuals"])

    assert result.exit_code == 0
    assert "'display_title': 'manuals'" in result.output


def test_api_prints_version(runner):
    result = runner.invoke(api.run_api, ["--version"])

    assert result.exit_code == 0
    assert re.match(r"^docstore, version \d+\.\d+\.\d+\n$", result.output)


@pytest.mark.parametrize("view_option", ["table", "grid"])
def test_sets_default_view_option(runner, store_root, view_option):
    result = runner.invoke(api.run_api, [
        str(store_root), "--default_view", view_option])
    assert result.exit_code == 0
    assert "'default_view': %r" % view_option in result.output


def test_unrecognised_view_option_is_rejected(runner, store_root):
    result = runner.invoke(api.run_api, [str(store_root), "--default_view", "mosaic"])
    assert result.exit_code == 2


@pytest.mark.parametrize("tag_view_option", ["cloud", "list"])
def test_sets_default_tag_view_option(runner, store_root, tag_view_option):
    result = runner.invoke(api.run_api, [
        str(store_root), "--tag_view", tag_view_option])
    assert result.exit_code == 0
    assert "'tag_view': %r" % tag_view_option in result.output


def test_unrecognised_tag_view_is_rejected(runner, store_root):
    result = runner.invoke(api.run_api, [str(store_root), "--tag_view", "mosaic"])
    assert result.exit_code == 2


class TestMigrations:
    def test_changes_checksums_to_sha256(self, runner, store_root):
        json_string = json.dumps({
            "1": {"name": "alex"},
            "2": {"name": "lexie", "sha256_checksum": "abcdef"},
            "3": {"name": "carol", "sha256_checksum": "ghijkl", "checksum": "xyz"}
        })

        db_root = store_root / "documents.json"
        db_root.open("w").write(json_string)

        runner.invoke(api.run_api, [str(store_root)])

        expected_data = {
            "1": {"name": "alex"},
            "2": {"name": "lexie", "checksum": "sha256:abcdef"},
            "3": {"name": "carol", "sha256_checksum": "ghijkl", "checksum": "xyz"}
        }

        actual_data = json.load(db_root.open())

        assert actual_data == expected_data
