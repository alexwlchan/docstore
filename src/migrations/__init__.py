# -*- encoding: utf-8

from .migration_001_sha256_checksum_field import replace_sha256_checksum_with_generic_field


ALL_MIGRATIONS = [
    replace_sha256_checksum_with_generic_field
]


def apply_migrations(object_store):
    for i, migration in enumerate(ALL_MIGRATIONS, start=1):
        print("Running migration %03d: %s" % (i, migration.__doc__), flush=True)
        migration(object_store)

    print("\n✨ Migrations complete! ✨", flush=True)
