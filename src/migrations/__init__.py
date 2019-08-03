# -*- encoding: utf-8

import logging

from .migration_001_sha256_checksum_field import replace_sha256_checksum_with_generic_field


logger = logging.Logger(__name__)


def apply_migrations(object_store):
    logger.info("Applying migrations to object store %r", object_store)

    logger.debug("Replacing 'sha256_checksum' field with 'checksum'")
    replace_sha256_checksum_with_generic_field(object_store)
