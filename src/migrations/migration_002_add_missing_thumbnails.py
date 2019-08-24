# -*- encoding: utf-8
"""
If there isn't a "thumbnail_identifier" on a record, try to create a thumbnail
and add it to a record.
"""

import sys

import tqdm

from file_manager import FileManager, ThumbnailManager


def add_missing_thumbnails(root, object_store):
    """Add missing thumbnails to documents"""
    missing_thumbnails = {
        obj_id: obj_data
        for obj_id, obj_data in object_store.objects.items()
        if "thumbnail_identifier" not in obj_data and "file_identifier" in obj_data
    }

    if missing_thumbnails:
        updated_objects = {}

        # TODO: This repeats a lot of code from api.py.  At some point it would
        # be nice to consolidate some of this.
        file_manager = FileManager(root / "files")
        thumbnail_manager = ThumbnailManager(root / "thumbnails")

        for obj_id, obj_data in tqdm.tqdm(missing_thumbnails.items()):
            absolute_file_identifier = file_manager.root / obj_data["file_identifier"]

            try:
                obj_data["thumbnail_identifier"] = thumbnail_manager.create_thumbnail(
                    obj_id,
                    absolute_file_identifier
                )
            except Exception as exc:
                print(
                    f"Error creating thumbnail for {absolute_file_identifier}: {exc}",
                    file=sys.stderr
                )
            else:
                updated_objects[obj_id] = obj_data

        object_store.write(updated_objects)
        print("")
