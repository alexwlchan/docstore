# -*- encoding: utf-8

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


def test_api_starts(runner, store):
    result = runner.invoke(api.run_api, [store.root])

    assert result.exit_code == 0
    assert "Called run()" in result.output
    assert ("root=%r" % store.root) in result.output


def test_api_sets_title(runner, store):
    result = runner.invoke(api.run_api, [store.root, "--title", "manuals"])

    assert result.exit_code == 0
    assert "'display_title': 'manuals'" in result.output


def test_api_prints_version(runner):
    result = runner.invoke(api.run_api, ["--version"])

    assert result.exit_code == 0
    assert re.match(r"^docstore, version \d+\.\d+\.\d+\n$", result.output)


@pytest.mark.parametrize("view_option", ["table", "grid"])
def test_sets_default_view_option(runner, store, view_option):
    result = runner.invoke(api.run_api, [store.root, "--default_view", view_option])
    assert result.exit_code == 0
    assert "'default_view': %r" % view_option in result.output


def test_unrecognised_view_option_is_rejected(runner, store):
    result = runner.invoke(api.run_api, [store.root, "--default_view", "mosaic"])
    assert result.exit_code == 2
