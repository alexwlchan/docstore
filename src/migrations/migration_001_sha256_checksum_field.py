# -*- encoding: utf-8
"""
Replace the algorithm-specific field:

    "sha256_checksum": "abcd..."

with a generic "checksum" field that includes an algorithm:

    "checksum": "sha256:abcd..."

"""

import tqdm


def replace_sha256_checksum_with_generic_field(root, object_store):
    """Replace the sha256_checksum field with the checksum field"""
    objects_to_migrate = {
        obj_id: obj_data
        for obj_id, obj_data in object_store.objects.items()
        if "sha256_checksum" in obj_data and "checksum" not in obj_data
    }

    if objects_to_migrate:
        updated_objects = {}

        for obj_id, obj_data in tqdm.tqdm(objects_to_migrate.items()):
            checksum_value = obj_data.pop('sha256_checksum')
            obj_data["checksum"] = f"sha256:{checksum_value}"
            updated_objects[obj_id] = obj_data

        object_store.write(updated_objects)
        print("")
