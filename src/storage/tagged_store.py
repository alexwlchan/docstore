# -*- encoding: utf-8

from .object_store import JsonObjectStore, MemoryObjectStore, ObjectStore


class TaggedObjectStore(ObjectStore):
    """
    A store for working with Python objects that support .get("tags", []).

    This store adds the ability to find objects that match a tag query.

    """
    def _matches_tag_query(self, obj, tag_query):
        tags = set(obj.get("tags", []))
        return all(q in tags for q in tag_query)

    def query(self, tag_query):
        return {
            obj_id: obj
            for obj_id, obj in self.objects.items()
            if self._matches_tag_query(obj, tag_query=tag_query)
        }


class MemoryTaggedObjectStore(MemoryObjectStore, TaggedObjectStore):
    pass


class JsonTaggedObjectStore(JsonObjectStore, TaggedObjectStore):
    pass
