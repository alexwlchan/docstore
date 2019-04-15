# CHANGELOG

## v1.1.0 - 2019-04-14

*   URLs in the list view are now relative URLs rather than absolute URLs.
    This means you can run the app behind a path prefix and everything will work fine.

*   If you specify a `filename` when you upload a document, set the appropriate `Content-Disposition` header when you retrieve the file.
    This means you can download a file with its original name.

## v1.0.0 - 2019-04-14

Initial tagged version.
