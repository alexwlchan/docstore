# -*- encoding: utf-8

import os
import pathlib

import docopt
import pytest

import cli
from config import DocstoreConfig


def test_cli_needs_root():
    with pytest.raises(docopt.DocoptExit):
        cli.parse_args("docstore", version="1.2.3", argv=[])


def test_cli_starts_with_just_root():
    config = cli.parse_args("docstore", version="1.2.3", argv=["/path/to/docstore"])

    assert isinstance(config, DocstoreConfig)
    assert config.root == pathlib.Path("/path/to/docstore")


def test_cli_root_is_abspath():
    config = cli.parse_args("docstore", version="1.2.3", argv=["docstore"])

    assert isinstance(config, DocstoreConfig)
    assert config.root == pathlib.Path(os.path.normpath("docstore"))


def test_default_title():
    config = cli.parse_args("docstore", version="1.2.3", argv=["/path/to/docstore"])

    assert config.title == "docstore"


def test_cli_sets_title():
    config = cli.parse_args(
        "docstore",
        version="1.2.3",
        argv=["/path/to/docstore", "--title", "my docstore instance"]
    )

    assert config.title == "my docstore instance"


def test_cli_prints_version(capsys):
    with pytest.raises(SystemExit):
        cli.parse_args("docstore", version="1.2.3", argv=["--version"])

    captured = capsys.readouterr()
    assert captured.out.strip() == "1.2.3"


def test_default_list_view_is_table():
    config = cli.parse_args("docstore", version="1.2.3", argv=["/path/to/docstore"])

    assert config.list_view == "table"


@pytest.mark.parametrize("list_view", ["table", "grid"])
def test_sets_list_view_option(list_view):
    config = cli.parse_args(
        "docstore",
        version="1.2.3",
        argv=["/path/to/docstore", "--default_view", list_view]
    )

    assert config.list_view == list_view


@pytest.mark.parametrize("list_view", ["cloud", "xyz", "mosaic"])
def test_unrecognised_list_view_is_rejected(list_view):
    with pytest.raises(
        docopt.DocoptExit,
        match=f"Unrecognised argument for --default_view: {list_view}"
    ):
        cli.parse_args(
            "docstore",
            version="1.2.3",
            argv=["/path/to/docstore", "--default_view", list_view]
        )


def test_default_tag_view_is_list():
    config = cli.parse_args("docstore", version="1.2.3", argv=["/path/to/docstore"])

    assert config.tag_view == "list"


@pytest.mark.parametrize("tag_view", ["cloud", "list"])
def test_sets_tag_view_option(tag_view):
    config = cli.parse_args(
        "docstore",
        version="1.2.3",
        argv=["/path/to/docstore", "--tag_view", tag_view]
    )

    assert config.tag_view == tag_view


@pytest.mark.parametrize("tag_view", ["grid", "table", "xyz", "mosaic"])
def test_unrecognised_tag_view_is_rejected(tag_view):
    with pytest.raises(
        docopt.DocoptExit,
        match=f"Unrecognised argument for --tag_view: {tag_view}"
    ):
        cli.parse_args(
            "docstore",
            version="1.2.3",
            argv=["/path/to/docstore", "--tag_view", tag_view]
        )
