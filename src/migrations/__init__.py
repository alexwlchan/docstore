# -*- encoding: utf-8

from .migration_001_sha256_checksum_field import replace_sha256_checksum_with_generic_field


def apply_migrations(object_store):
    replace_sha256_checksum_with_generic_field(object_store)
