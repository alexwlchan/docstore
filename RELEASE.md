RELEASE_TYPE: minor

This release makes it easier to change the document view (table/grid) and to change the sort order of documents (by title or date added).  There are new menus in the top navbar for controlling both options.

It also fixes a pair of bugs:

*   If you're filtering by a tag, you can't select a second filter for it in the list of tags
*   The app correctly remembers if you had the new document form and/or tag browser expanded, where previously it would forget
*   It fixes an internal error that could be thrown when creating thumbnails from unusual file formats

Plus more internal refactoring and extra tests.
