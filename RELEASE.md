RELEASE_TYPE: patch

Fix a bug introduced in v1.14.3 that meant the container would never start.

Also add `mimetype` to the Docker image, which fixes a crash when trying to create thumbnails for some file formats (e.g. Markdown).