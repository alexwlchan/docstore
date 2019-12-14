RELEASE_TYPE: patch

Fix a bug in v1.20.x where deleting a document from the UI wouldn't work if you were running docstore under a path, e.g. `https://example.net/docstore`.