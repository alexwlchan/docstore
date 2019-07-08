RELEASE_TYPE: minor

This release changes the underlying storage to be more human-readable.

Rather than storing files with an opaque UUID, they are now named with a normalised version of their original filename (if supplied).  The original, un-normalised filename is still stored in the database and returned in the `Content-Disposition` header.  If you don't supply an original filename in the upload, it uses a UUID as before.

If you want to migrate an existing docstore instance to use the more human-readable filenames, there's a (lightly tested) migration script `migrations/use_human_friendly_filenames.py` in the root of this repo.
