# CHANGELOG

## v1.20.3 - 2019-12-14

Internal refactoring.

Specifically, I'm using `humanize.naturaltime` from the [humanize module](https://pypi.org/project/humanize/), rather than hand-rolling my own code for printing date strings.  Less code for me to maintain!

## v1.20.2 - 2019-12-14

Fix a bug in v1.20.x where deleting a document from the UI wouldn't work if you were running docstore under a path, e.g. `https://example.net/docstore`.

## v1.20.1 - 2019-12-13

Fix a cosmetic bug introduced in v1.20.0.

## v1.20.0 - 2019-12-13

If you use the new "actions" menu, there's an option to delete documents directly from the UI, which is something I've wanted for a while.

(As with calling the HTTP endpoint, this is only a "soft" delete -- the files are moved to a separate folder and disappear from the main view, but nothing is deleted from disk.)

## v1.19.1 - 2019-11-26

Tweak a bit of wording in the UI.

## v1.19.0 - 2019-11-24

If you're using the web app, it offers to autocomplete tags used in the current
context (that is, tags used by other documents on the same page).  This should
reduce typing and ensure more consistent tagging.

## v1.18.0 - 2019-11-24

Add an option to set the page size in the GUI app.

By default, docstore shows 250 documents per page.  You can change the number of
documents on each page by passing the `--page_size` flag (for example, to reduce
the number of thumbnails if you have lots of animated GIFs).

## v1.17.2 - 2019-10-12

Fix a bug where new thumbnails wouldn't reload until you restarted the app.

## v1.17.1 - 2019-09-29

Remove a stray debugging line from 1.17.0.

## v1.17.0 - 2019-09-29

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

## v1.16.6 - 2019-09-26

Use gunicorn to run the server, not the Flask debug server (which isn't intended for production apps).

## v1.16.5 - 2019-09-25

This is an internal refactor to replace responder/requests with Flask.  There should be no user-visible changes.

## v1.16.4 - 2019-09-19

Improve the look of thumbnails in the grid view that don't have a title.

## v1.16.3 - 2019-08-30

Cosmetic tweak: use curly quotes/Smartypants when displaying the title of a docstore insatnce.

## v1.16.2 - 2019-08-29

Fix a bug where alerts about new uploads weren't being dismissed correctly.

## v1.16.1 - 2019-08-29

Fix a pair of bugs around pagination, or "what should have been in v1.16.0".

*   Fix a bug where links in tag clouds weren't being coloured correctly
*   Page information is dropped when filtering/unfiltering by tag, so you won't get dropped on an empty page when clicking through to a tag

And two more miscellaneous bugfixes:

*   Use the accent colour in the pagination navbar
*   Fix the link in the

## v1.16.0 - 2019-08-29

Add support for pagination in the GUI app.

If you have more than 250 documents, they get broken into pages to reduce the number of items on each page (and so making the app faster and more responsive!).

## v1.15.0 - 2019-08-28

This release makes it easier to change the document view (table/grid) and to change the sort order of documents (by title or date added).  There are new menus in the top navbar for controlling both options.

It also fixes a pair of bugs:

*   If you're filtering by a tag, you can't select a second filter for it in the list of tags
*   The app correctly remembers if you had the new document form and/or tag browser expanded, where previously it would forget
*   It fixes an internal error that could be thrown when creating thumbnails from unusual file formats

Plus more internal refactoring and extra tests.

## v1.14.4 - 2019-08-28

Fix a bug introduced in v1.14.3 that meant the container would never start.

Also add `mimetype` to the Docker image, which fixes a crash when trying to create thumbnails for some file formats (e.g. Markdown).

## v1.14.3 - 2019-08-28

More internal refactoring, this time to use docopt instead of CLI for the command-line parsing.

## v1.14.2 - 2019-08-26

More internal refactoring to improve the speed of the test suite.

## v1.14.1 - 2019-08-26

This is an internal refactoring that tidies up some of the code and should make testing easier. No user-visible changes.

## v1.14.0 - 2019-08-24

Remove the `/api/v1/recreate_thumbnails` endpoint, because I wasn't using it.

## v1.13.7 - 2019-08-24

Improve the reporting of database migrations (so you'll see if docstore isn't starting because one is running), and try to recreate missing thumbnails on startup.

## v1.13.6 - 2019-08-15

This changes the way database migrations work, so they should be a lot faster and properly atomic.  When you start an instance docstore and it needs to run a migration, the web server should start a lot faster.

## v1.13.5 - 2019-08-09

Another tweak to reduce the size of the final image.  This takes the size of the image from 518MB to 322MB.

## v1.13.4 - 2019-08-09

This fixes a small bug in the tag list if you had a heavily nested hierarchy of tags, where the hierarchy wouldn't de-nest correctly.

For example, you could see the following incorrect nesting where `delta` is indented too far:

    - alfa
      - alfa:bravo
        - alfa:bravo:charlie
      - delta

It also cleans up the display of tags, so rather than the above you'd see:

    - alfa
      - bravo
        - charlie
    - delta

This indicates four tags: `alfa`, `alfa:bravo`, `alfa:bravo:charlie` and `delta`, but with less repetition.

This new version is based on code [from Dreamwidth](https://github.com/dreamwidth/dw-free/blob/6ec1e146d3c464e506a77913f0abf0d51a944f95/styles/core2.s2#L4126).

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
