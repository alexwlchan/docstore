# docstore

This is a small Python web app for managing my scanned documents.

I wanted a way to upload PDFs, add a few tags, then filter by those tags.
It includes small thumbnails to help me identify images.

![](screenshot.png)

It was a chance for me to play with [Responder](https://github.com/kennethreitz/responder) and newer versions of [Bootstrap](https://getbootstrap.com/) in a quick tool.

You can read some of what I learnt in the [what I learnt][what-i-learnt.md] file.



## Usage

Build the Docker image by running:

```console
$ make build
```

Then start the app by running:

```console
$ docker run --detach --publish 8072:8072 --volume $(pwd)/documents:/documents docstore
```

To view your documents, open <http://localhost:8072> in a browser.



## Uploading documents

To index a PDF document, make a POST request to `/upload`:

```http
POST /upload
{
  "file": "<Body of PDF file to store>",
  "title": "My great document",
  "tags": "tag1 tag2 tag3",
  "filename": "Document1.pdf",
  "sha256_checksum": "<SHA256 checksum of PDF>"
}
```

Required parameters:

*   `file` -- the contents of the PDF file to store, sent as an HTTP multipart request

Optional parameters:

*   `title` -- the title of the document to display in the viewer.
*   `tags` -- a list of tags to apply to the document.
*   `filename` -- the name of the original PDF file.
*   `sha256_checksum` -- the SHA256 checksum of the original file.
    The upload will fail if the checksum does not match the upload file.

Extra parameters in the request will also be stored in the database, although they aren't used by the viewer right now.

This will return a 201 Created if the upload succeeds, or a 400 Bad Request if not.
For the latter, the body of the response will include an explanation, for example:

```http
POST /upload
400 Bad Request
{
  "error": "The SHA256 checksum (123…abc) does not match the checksum of the uploaded document (456…def)."
}
```

For one implementation of this upload API, see the `bin/index_document.py` script in the repo.



## License

MIT.
