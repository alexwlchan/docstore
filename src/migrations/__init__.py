# -*- encoding: utf-8

from .migration_001_sha256_checksum_field import replace_sha256_checksum_with_generic_field
from .migration_002_add_missing_thumbnails import add_missing_thumbnail


ALL_MIGRATIONS = [
    replace_sha256_checksum_with_generic_field,
    add_missing_thumbnail,
]


def apply_migrations(root, object_store):
    for i, migration in enumerate(ALL_MIGRATIONS, start=1):
        print("Running migration %03d: %s" % (i, migration.__doc__), flush=True)
        migration(root=root, object_store=object_store)

    print("✨ Migrations complete! ✨", flush=True)
