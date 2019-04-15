# CHANGELOG

## v1.1.1 - 2019-04-15

*   If it can't detect a file extension from the data, it throws an error rather than failing silently.
    Pass an explicit `filename` if this happens.

*   Rudimentary support for creating thumbnails from EPUB files.

## v1.1.0 - 2019-04-14

*   URLs in the list view are now relative URLs rather than absolute URLs.
    This means you can run the app behind a path prefix and everything will work fine.

*   If you specify a `filename` when you upload a document, set the appropriate `Content-Disposition` header when you retrieve the file.
    This means you can download a file with its original name.

## v1.0.0 - 2019-04-14

Initial tagged version.
