# CHANGELOG

## v1.13.3 - 2019-08-09

Fix a tiny cosmetic bug where selecting a tag in the document list would cause the spacing of the tags to change.

## v1.13.2 - 2019-08-04

Improve the user documentation, and change the default title from "Alex's documents" to "docstore".

## v1.13.1 - 2019-08-03

The Docker image is now significantly smaller (482MB rather than 832MB).

This is because it's now using `alpine` as its base image, rather than `python/3.6-jessie`.

## v1.13.0 - 2019-08-03

docstore now stores checksums in a different format.  Previously it wrote a field like:

```json
{
  ...
  "sha256_checksum": "abc...def"
}
```

It now writes a field `"checksum"` with the algorithm prepended, for example:

```json
{
  ...
  "checksum": "sha256:abc...def"
}
```

which is more future-proof if I ever decide to change the checksum algorithm.

Old databases will be migrated to the new format when you first run a release with the new code.

## v1.12.1 - 2019-08-03

Add a link to the GitHub repo in the footer.

## v1.12.0 - 2019-08-03

docstore no longer checks the `"sha256_checksum"` value in a POST request to `/upload`.

As far as I know, nobody is routinely uploading documents with this field, so it's simpler to take it out.  I upload all my documents through the web interface, and it doesn't send this value.

If you do send a value for `"sha256_checksum"`, it will be stored in the database separate to the one that gets computed by docstore, like so:

```json
{
  ...
  "sha256_checksum": "<computed by docstore>",
  "user_data": {
    "sha256_checksum": "<sent in the POST request>"
  }
}
```

If you want to check it, you'll need to check the database with your own code.

## v1.11.8 - 2019-07-29

The app now creates thumbnails for some PDFs where previously thumbnail creation would fail.

Specifically, it now includes `qpdf`, which is used by the preview-generator library to create thumbnails of some PDFs.

## v1.11.7 - 2019-07-28

Static assets (files, thumbnails) now specify a much longer caching time, which should improve performance.

## v1.11.6 - 2019-07-27

Fix a cosmetic bug introduced in v1.11.4 where special characters would be displayed as unescaped, e.g. `It&#8217;s time for your next eye test` instead of `It’s time for your next eye test`.

## v1.11.5 - 2019-07-27

Fix a bug where the version in the footer would always show the previous version, not the current version.

## v1.11.4 - 2019-07-23

Titles in the document list are now rendered with [SmartyPants](https://daringfireball.net/projects/smartypants/), including curly quotes and nice dashes.

## v1.11.3 - 2019-07-08

Fix a tiny cosmetic issue in the display of tags on an individual document.

## v1.11.2 - 2019-07-08

Fix a bug that meant thumbnails weren't being created in v1.11.x.

## v1.11.1 - 2019-07-08

Fix a cosmetic bug in the grid view with items that had a very small vertical height -- hovering over to see the info panel would obscure the entire thumbnail, and make it impossible to click through!

## v1.11.0 - 2019-07-08

This release changes the underlying storage to be more human-readable.

Rather than storing files with an opaque UUID, they are now named with a normalised version of their original filename (if supplied).  The original, un-normalised filename is still stored in the database and returned in the `Content-Disposition` header.  If you don't supply an original filename in the upload, it uses a UUID as before.

If you want to migrate an existing docstore instance to use the more human-readable filenames, there's a (lightly tested) migration script `scripts/use_human_friendly_filenames.py` in the root of this repo.

## v1.10.5 - 2019-07-07

Internal documentation improvement.

## v1.10.4 - 2019-07-06

Styling improvements:

*   More consistency, less box shadows on the cards for each document
*   The "add document" button now uses your accent colour
*   The tag filter info box is grey, not a weird blue
*   The "new document added" alert is now dismissable
*   Tweak the appearance of the tag list and metadata

## v1.10.3 - 2019-07-02

Change the behaviour of the underlying JSON parser so it picks up changes to the database file if edited outside the application.

## v1.10.2 - 2019-07-02

This fixes a bug where links to tags with ampersands (`&`) would be broken.

See [alexwlchan/docstore#60](https://github.com/alexwlchan/docstore/issues/60).

## v1.10.1 - 2019-07-02

Improve the thumbnails you get from EPUB ebook files.

In particular, it's now inspecting the EPUB manifest, which means it's smarter
about finding a cover image, not just the largest image in the book.

## v1.10.0 - 2019-07-01

Add support for creating thumbnails from MOBI ebook files.

## v1.9.1 - 2019-06-30

Fix a bug where tags in the table view would wrap unnecessarily.

## v1.9.0 - 2019-06-30

This is a major refactor of the viewer.  Everything now uses CSS Grid (inspired by a CodePen [by Olivia Ng](https://codepen.io/oliviale/pen/WqwOzv)) and has a more consistent layout.  The underlying code is much simpler, yay.

The new design also works much better on smaller screens.

I've removed the buttons for changing the sort order because I wasn't using them.  The old URL query parameters will still work, but I'll probably delete them later.

## v1.8.0 - 2019-06-30

This adds two flags for the GUI viewer:

*   `--tag_view=(cloud|list)` allows you to select a tag cloud-like view in "View Tags", which displays tags bigger if they're more common, rather than a flat list.

*   `--accent_color=#aabbcc` allows you to set an accent colour for the GUI style.  This isn't used much (yet), but gets rid of some of the blue!

## v1.7.7 - 2019-06-16

This fixes a bug introduced in v1.7.6, where trying to store a document while running inside a Docker container could throw an error:

```
OSError: [Errno 18] Invalid cross-device link
```

## v1.7.6 - 2019-06-16

Further refactoring of the underlying code to make it simpler and easier to work with.

## v1.7.5 - 2019-06-09

This is a big internal refactoring to make the code easier to work with and easier to test, but with no user-facing changes.  At best, there should be some mild performance improvements.

## v1.7.4 - 2019-06-08

This is a minor rearrangement of the Git repo to make it a bit easier to work on docstore.

There should be no user-visible effect, except that tests are no longer included in the Docker image (so it should be a shade smaller).

## v1.7.3 - 2019-05-27

Fix two bugs related to the source URL field in the web app:

*   Only display the source link if the database has a non-empty value; don't display an empty link
*   Only store values in the database if they're non-empty; don't store empty strings

## v1.7.2 - 2019-05-27

Bump the versions of bundled dependencies.

## v1.7.1 - 2019-05-27

Internal refactoring and code cleanups.  This should have no user-visible effect.

Details:

*   Use pathlib.Path for handling paths internally, not strings
*   Some of the internal methods were renamed to reduce ambiguity
*   Removing an internal model in favour of a plain dict
*   Better tests around the GUI viewer
*   Checking the SHA256 checksum of a file doesn't read the whole file at once, which should be more memory efficient

## v1.7.0 - 2019-05-07

Change the internal data format so we don't store the document ID twice.

This means the `"id"` won't be written to the body of the JSON value for
a document, just stored in the database key.

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
