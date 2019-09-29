RELEASE_TYPE: minor

Add the ability to soft delete documents by making an HTTP DELETE:

```http
DELETE /documents/{doc_id}
```

```http
200 OK
{"deleted": "ok"}
```

This will remove the documents from the database, and hide them from the web app -- but the data is still kept on disk.  There's a new folder `deleted` alongside `files` and `thumbnails` in the docstore root, and deleted data is saved there.
You have to delete those files outside docstore.
