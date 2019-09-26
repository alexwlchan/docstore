RELEASE_TYPE: patch

Use gunicorn to run the server, not the Flask debug server (which isn't intended for production apps).