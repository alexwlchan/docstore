# CHANGELOG

## v1.2.1 - 2019-04-21

*   Tiny cosmetic tweak to make the "filtering by tag X" blurb more promionent.

## v1.2.0 - 2019-04-19

*   Add a GUI form for storing a document in the web app, so you can upload new documents through the browser.

*   Display version information in the footer.

*   The tag list and "store a document" forms are both stateful, so if you reload the page your toggle position will be preserved.

## v1.1.2 - 2019-04-17

*   Fix a bug where the "date added" header wasn't always shown in the table view, and you couldn't sort by date.

*   Use relative links for the sort order and view order, so they work when running behind a path prefix.

*   Display version information in the footer of the browser.

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
