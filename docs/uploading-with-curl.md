# Uploading documents with curl

You can upload documents by making a POST request to `/upload`.

[curl](https://curl.haxx.se/) is a command-line tool for making HTTP requests.
You can upload a document using curl with the following command:

```
curl \
  -F 'file=@kallax.pdf' \
  -F 'title=Kallax shelf instructions' \
  -F 'tags=furniture ikea' \
  -F 'source_url=https://ikea.com/manuals/kallax.pdf' \
  http://localhost:8072/upload
```

The `file` parameter is required, and should be `@` followed by the path to the file you want to upload.

All other parameters are optional.
The `title`, `tags` and `source_url` parameters are used in the web app.
If you include extra parameters, they will also be stored in the database, but not shown in the web app.

This will return a 201 Created if the upload succeeds, or a 400 Bad Request if not.
In the latter case, the body of the response will include an explanation.
For example, if you omit the `file` parameter:

```http
POST /upload
400 Bad Request
{
  "error": "Unable to find multipart upload 'file'!"
}
```
