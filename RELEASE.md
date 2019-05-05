RELEASE_TYPE: minor

This patch improves the thumbnail generator, by using ImageMagick rather than Pillow for image resizing.  Thumbnail creation is a bit slower but higher quality.

It also adds a new API endpoint, for triggering the recreation of all the existing thumbnails with the new code:

```http
POST /api/v1/recreate_thumbnails
```