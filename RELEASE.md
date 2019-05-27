RELEASE_TYPE: patch

Internal refactoring and code cleanups.  This should have no user-visible effect.

Details:

*   Use pathlib.Path for handling paths internally, not strings
*   Some of the internal methods were renamed to reduce ambiguity
*   Removing an internal model in favour of a plain dict
*   Better tests around the GUI viewer
*   Checking the SHA256 checksum of a file doesn't read the whole file at once, which should be more memory efficient
