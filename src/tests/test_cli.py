# -*- encoding: utf-8

import subprocess
import time

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
