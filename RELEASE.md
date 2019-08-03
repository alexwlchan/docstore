RELEASE_TYPE: patch

The Docker image is now significantly smaller (482MB rather than 832MB).

This is because it's now using `alpine` as its base image, rather than `python/3.6-jessie`.
