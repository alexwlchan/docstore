RELEASE_TYPE: patch

The app now creates thumbnails for some PDFs where previously thumbnail creation would fail.

Specifically, it now includes `qpdf`, which is used by the preview-generator library to create thumbnails of some PDFs.
