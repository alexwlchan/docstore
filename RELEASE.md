RELEASE_TYPE: minor

Add an option to set the page size in the GUI app.

By default, docstore shows 250 documents per page.  You can change the number of
documents on each page by passing the `--page_size` flag (for example, to reduce
the number of thumbnails if you have lots of animated GIFs).
