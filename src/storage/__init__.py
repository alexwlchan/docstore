# -*- encoding: utf-8

from .exceptions import NoSuchObject
from .object_store import JsonObjectStore, MemoryObjectStore, ObjectStore
from .tagged_store import (
    JsonTaggedObjectStore,
    MemoryTaggedObjectStore,
    TaggedObjectStore
)

__all__ = [
    "NoSuchObject",

    "JsonObjectStore",
    "MemoryObjectStore",
    "ObjectStore",

    "JsonTaggedObjectStore",
    "MemoryTaggedObjectStore",
    "TaggedObjectStore",
]
