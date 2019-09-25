# -*- encoding: utf-8

import pathlib
import random
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent / "src"))

import api  # noqa
import config  # noqa
from storage import MemoryTaggedObjectStore  # noqa


def create_app(
    *,
    store_root,
    tagged_store=None,
    title=None,
    list_view=None,
    tag_view=None,
    accent_color=None
):
    tagged_store = tagged_store or MemoryTaggedObjectStore(initial_objects={})
    title = title or "test docstore instance"
    list_view = list_view or random.choice(["table", "grid"])
    tag_view = tag_view or random.choice(["list", "cloud"])
    accent_color = accent_color or "#ff0000"

    docstore = api.Docstore(
        tagged_store=tagged_store,
        config=config.DocstoreConfig(
            root=store_root,
            title=title,
            list_view=list_view,
            tag_view=tag_view,
            accent_color=accent_color
        )
    )

    # See https://flask.palletsprojects.com/en/1.1.x/testing/#the-testing-skeleton:
    #
    #   What [setting this flag] does is disable error catching during
    #   request handling, so that you get better error reports when performing
    #   test requests against the application.
    #
    docstore.app.config['TESTING'] = True

    return docstore.app.test_client()
