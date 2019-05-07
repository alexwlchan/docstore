RELEASE_TYPE: minor

Change the internal data format so we don't store the document ID twice.

This means the `"id"` won't be written to the body of the JSON value for a document, but it won't remove the `"id"` field from existing documents.
