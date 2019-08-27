# -*- encoding: utf-8

import os
import pathlib

import docopt

from config import DocstoreConfig


def parse_args(prog, *, version, argv):
    help_string = f"""Usage: {prog} <root> [options]

    --title=<TITLE>                 Title to display in the header.  [default: docstore]
    --default_view=(table|grid)     How to display documents in the viewer.
                                    [default: table]
    --tag_view=(list|cloud)         How to display the list of tags on a page.
                                    [default: list]
    --accent_color=<COLOR>          The tint color for links and tags.
                                    [default: #007bff]
    """

    args = docopt.docopt(help_string, argv=argv, version=version)

    if args["--default_view"] not in {"table", "grid"}:
        raise docopt.DocoptExit(
            f"Unrecognised argument for --default_view: {args['--default_view']}"
        )

    if args["--tag_view"] not in {"list", "cloud"}:
        raise docopt.DocoptExit(
            f"Unrecognised argument for --tag_view: {args['--tag_view']}"
        )

    return DocstoreConfig(
        root=pathlib.Path(os.path.normpath(args["<root>"])),
        title=args["--title"],
        list_view=args["--default_view"],
        tag_view=args["--tag_view"],
        accent_color=args["--accent_color"]
    )
