# -*- encoding: utf-8

from .exceptions import AlreadyExistsError, NoSuchObject
from .object_store import JsonObjectStore, MemoryObjectStore, ObjectStore
from .tagged_store import (
    JsonTaggedObjectStore,
    MemoryTaggedObjectStore,
    TaggedObjectStore
)

__all__ = [
    "AlreadyExistsError",
    "NoSuchObject",

    "JsonObjectStore",
    "MemoryObjectStore",
    "ObjectStore",

    "JsonTaggedObjectStore",
    "MemoryTaggedObjectStore",
    "TaggedObjectStore",
]
