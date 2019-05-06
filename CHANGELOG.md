# CHANGELOG

## v1.6.0 - 2019-05-06

Add a `--port` flag for selecting the port to run the web app on.

## v1.5.0 - 2019-05-06

This patch improves the thumbnail generator, by using ImageMagick rather than Pillow for image resizing.  Thumbnail creation is a bit slower but higher quality.  A nice side effect is that you can now get thumbnails for animated GIFs



It also adds a new API endpoint, for triggering the recreation of all the existing thumbnails with the new code:



```http

POST /api/v1/recreate_thumbnails

```

## v1.4.1 - 2019-05-05

Styling and design tweaks in the UI, but no functional changes.

## v1.4.0 - 2019-04-30

Add a `--view_option` flag to the CLI, which allows you to decide whether the table or grid view should be the default view.

## v1.3.6 - 2019-04-30

Don't require a title to be set in the web GUI form.

## v1.3.5 - 2019-04-24

Swap the order of the "Store a document" and "Show tags" form, so the former always appears in a consistent position.

## v1.3.4 - 2019-04-23

Tweak the display of dates in the table UI to avoid line wrapping.

## v1.3.3 - 2019-04-23

Change some of the internal storage logic so it's less likely to return a user error or server error when trying to index documents.



Specifically, change the logic for detecting filename extensions (which are mostly used for internal storage), and just don't set one if it can't be detected.

## v1.3.2 - 2019-04-21

Tweak the URL handling so you can open links in new tabs/windows.

## v1.3.1 - 2019-04-21

Fix a bug where tags with URL-encoded characters would be displayed incorrectly in the "store a document" form.

## v1.3.0 - 2019-04-21

Add a "source URL" field to the web form and index document script, and display it in the web UI.

This makes it easier to track the original source of a document.

## v1.2.2 - 2019-04-21

*   Fix a tiny cosmetic issue when hovering over tag links on a document.

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
