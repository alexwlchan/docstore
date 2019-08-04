# docstore

[![Build Status](https://dev.azure.com/alexwlchan/alexwlchan/_apis/build/status/alexwlchan.docstore?branchName=development)](https://dev.azure.com/alexwlchan/alexwlchan/_build/latest?definitionId=4&branchName=development)

This is a small Python web app for managing my scanned documents and other files.

You can upload files through a web UI or HTTP endpoint, add a few tags, then filter by those tags.
It includes small thumbnails to help identify files.

![](screenshot.png)

It was originally written for me to play with [Responder](https://github.com/kennethreitz/responder) and newer versions of [Bootstrap](https://getbootstrap.com/), and now I use it to store.

You can read some of what I learnt in the [what I learnt](what-i-learnt.md) file.



## Ideas

*   The underlying storage should be independent of my code.
    If all my code is thrown away, the data format should be simple enough for anybody to parse and interpret.

*   Filesystems get antsy about special characters, so better to store documents internally with UUID filenames, and store the original filename in the database.
    This can be surfaced with the `Content-Disposition` header when somebody downloads the image.

*   Code for storing documents should be very robust.  Practically speaking, that means:

    -   Test everything.  100% line and branch coverage as a minimum.
    -   SHA256 checksums throughout so you can detect file corruption.


## Usage

You need to install [Docker](https://hub.docker.com/search/?type=edition&offering=community) to run docstore.

Once you have Docker installed, you start docstore like so:

```console
$ docker run --publish 8072:8072 --volume /path/to/documents:/documents greengloves/docstore
```

Replace `/path/to/documents` with the name of a folder on your computer where you want docstore to keep its data.

This will start a web app, which you can view by opening <http://localhost:8072> in a browser.
Within the app, you can upload new files by clicking "Store a document", or browse your stored files.

I've written some documents that explain a bit about how to use docstore:

*   [Running docstore with Docker Compose](docs/docker-compose.md)
*   [Uploading documents with curl](docs/uploading-with-curl.md) -- how to upload documents if you don't want to use the web app.
    These instructions can be adapted for any tool that can make HTTP requests.
*   [Usage options](docs/usage.md) -- setting title, accent color, changing the port, and so on



## License

MIT.
