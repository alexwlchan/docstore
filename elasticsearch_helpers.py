#!/usr/bin/env python
# -*- encoding: utf-8

import copy
import datetime as dt

import elasticsearch


class DocumentIndex:

    def __init__(self):
        self.index_name = "documents" + dt.datetime.now().isoformat().lower()
        self.es = elasticsearch.Elasticsearch()

        self.es.indices.create(
            index=self.index_name,
            body={
                "mappings": {
                    self.index_name: {
                        "properties": {
                            "indexed_at": {"type": "date"},
                            "tags": {"type": "keyword"},
                            "name": {"type": "keyword"},
                        }
                    }
                }
            }
        )

    def index_document(self, doc):
        enriched_doc = copy.deepcopy(doc)
        enriched_doc["name"] = doc.get("title", doc["filename"])

        self.es.index(
            index=self.index_name,
            doc_type=self.index_name,
            id=doc["id"],
            body=enriched_doc
        )

    def search_documents(
        self,
        tags=None,
        include_tag_aggs=False,
        sort_order="indexed_at:desc"
    ):
        field, order = sort_order.split(":")
        body = {
            "sort": [
                {field: {"order": order}}
            ]
        }

        if include_tag_aggs:
            body["aggregations"] = {
                "tags": {
                    "terms": {
                        "field": "tags",
                        "size": 1000
                    },
                }
            }

        if tags:
            es_filter = {
                "bool": {
                    "must": [
                        {"term": {"tags": t}} for t in tags
                    ]
                }
            }
            body["query"] = {
                "bool": {"filter": es_filter}
            }

        return self.es.search(
            index=self.index_name,
            doc_type=self.index_name,
            body=body
        )

    def get_document(self, doc_id):
        return self.es.get(
            index=self.index_name,
            doc_type=self.index_name,
            id=doc_id
        )
