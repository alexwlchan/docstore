# What I learnt

The point of this project was to play with some new tools (responder, Bootstrap, more JavaScript).
I've learnt a bunch while doing the project, but it's hard to see it in one place.
There are inline comments that explain what a piece of code is doing, but they're scattered around the codebase.

For my benefit and for everybody else, this file has a short list of some of the things I learnt while working on docstore.
I'll add to the file as I learn more!

Contents:

*   [HTTP and web stuff](#http-and-web-stuff)

    -   [The Content-Disposition HTTP header](#the-content-disposition-http-header)
    -   [Manipulating URL query parameters in JavaScript](#manipulating-url-query-parameters-in-javascript)
    -   [Edit the URL in the window without reloading the page](#edit-the-url-in-the-window-without-reloading-the-page)
    -   [Construct the URL behind an &lt;a&gt; tag in JavaScript](#construct-the-url-behind-an-a-tag-in-javascript)

*   [Useful Python libraries and tricks](#useful-python-libraries-and-tricks)

    -   [whitenoise: for serving static files](#whitenoise-for-serving-static-files)
    -   [python-magic: detect the mimetype of some bytes](#python-magic-detect-the-mimetype-of-some-bytes)
    -   [mimetypes: get a filename extension for a mimetype](#mimetypes-get-a-filename-extension-for-a-mimetype)
    -   [preview-generator: creating thumbnails of files](#preview-generator-creating-thumbnails-of-files)
    -   [hyperlink: manipulate URL query parameters](#hyperlink-manipulate-URL-query-parameters)
    -   [Include the filename, content-type and content-length in a python-requests upload](#include-the-filename,-content-type-and-content-length-in-a-python-requests-upload)

*   [Everything else](#everything-else)

    -   [Getting the cover image of an epub file](#getting-the-cover-image-of-an-epub-file)



## HTTP and web stuff

### The Content-Disposition HTTP header

The `Content-Disposition` header can be used to tell a browser the filename of an HTTP response.
It's used for "Save As" or when downloading the file.

Because docstore stores documents with a UUID, the URLs it uses for files are of the form:

    /files/0/0645c33f-0be6-44e1-8059-228ec9594867.pdf

It includes a `Content-Disposition` header of the form:

    filename*=utf-8''original_filename.pdf

so if the browser navigates to that page and downloads the file, they get `original_filename.pdf`.

Read more:

*   MDN docs for Content-Disposition: <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition>
*   Encoding a filename as UTF-8: <https://stackoverflow.com/a/49481671/1558022>



### Manipulating URL query parameters in JavaScript

Last time I did this, I had to use some moderately fiddly code from Stack Overflow.
There are built-in tools for this now:

```javascript
function addQueryParameter(name, value) {
  var url = new URL(window.location.href);
  url.searchParams.append(name, value);
  return url.href
}

function setQueryParameter(name, value) {
  var url = new URL(window.location.href);
  url.searchParams.set(name, value);
  return url.href
}

function deleteQueryParameter(name) {
  var url = new URL(window.location.href);
  url.searchParams.delete(name);
  return url.href
}
```

All these methods return a string based on the current window location.
See <https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams>



### Edit the URL in the window without reloading the page

Yes, that's possible:

```javascript
window.history.pushState({path: newUrl }, "", newUrl);
```

You can also use `replaceState`, which overwrites the current history entry.
(I can't spot the difference in behaviour in Safari.)



### Construct the URL behind an &lt;a&gt; tag in JavaScript

Like so:

```html
<a href="#" onclick="window.location = setQueryParameter('color', 'blue');">
```

Useful if you're using the previous trick to edit the URL without reloading the page, so you have to construct new URLs dynamically.



## Useful Python libraries and tricks

### whitenoise: for serving static files

[whitenoise] is a Python library for serving static files in a WSGI application.
When you create an instance of whitenoise, you pass it a folder, and it learns all the files in that folder.
If you save a new file in that folder, you need to tell whitenoise about it.

Here's a quick example, taken from the [whitenoise docs][wn_docs]:

```python
from whitenoise import WhiteNoise

from my_project import MyWSGIApp

application = MyWSGIApp()
application = WhiteNoise(application, root='/path/to/static/files')
application.add_files('/path/to/more/static/files', prefix='more-files/')
```

It gets unhappy if the size of a file changes underneath it, after the initial load.

Read more:

*   Whitenoise docs: <http://whitenoise.evans.io/en/stable/>

[whitenoise]: https://pypi.org/project/whitenoise/
[wn_docs]: http://whitenoise.evans.io/en/stable/#quickstart-for-other-wsgi-apps



### python-magic: detect the mimetype of some bytes

[python-magic] is a library for detecting the mimetype of some bytes.
A simple example:

```python
import magic

assert isinstance(data, bytes)
guessed_mimetype = magic.from_buffer(data, mime=True)
```

[python-magic]: https://pypi.org/project/python-magic/



### mimetypes: get a filename extension for a mimetype

Once you have a mimetype from magic, you can use the [mimetypes] library to get an appropriate filename extension:

```python
import mimetypes

extension = mimetypes.guess_extension(guessed_mimetype)
```

Note that `guess_extension()` will pick the first filename extension, which may not always be what you want.
(See the [CPython implementation][guess_extension].)

In particular, it returns `.jpe` for JPEG images, so I special case it:

```python
if guessed_mimetype == "image/jpeg":
    extension = ".jpg"
else:
    extension = mimetypes.guess_extension(guessed_mimetype)
```

[mimetypes]: https://docs.python.org/3/library/mimetypes.html
[guess_extension]: https://github.com/python/cpython/blob/7e18deef652a9d413d5dbd19d61073ba7eb5460e/Lib/mimetypes.py#L179-L195



### preview-generator: creating thumbnails of files

I need to create thumbnail images of documents, and [preview-generator] has support for lots of common file types.

Here's a basic example:

```python
from preview_generator.manager import PreviewManager

manager = PreviewManager("/path/to/cache")
thumbnail_path = manager.get_jpeg_preview("/path/to/file.pdf")
```

It throws `preview_generator.exception.UnsupportedMimeType` if you try to get a thumbnail of a type it doesn't support (for example, epub).

It uses a bunch of external dependencies for reading files (inkscape, libreoffice, …).
You don't have to install them all, but it drops a bunch of warnings if it can't find them when you construct `PreviewManager`.
I'm being a bit naughty and suppressing them when I create the manager:

```python
class NoBuilderWarningFilter(logging.Filter):
    def filter(self, record):
        return False

logger = logging.getLogger(PREVIEW_GENERATOR_LOGGER_NAME)
f = NoBuilderWarningFilter()
logger.addFilter(f)
manager = PreviewManager(tempfile.mkdtemp())
logger.removeFilter(f)
```

[preview-generator]: https://pypi.org/project/preview-generator/



### hyperlink: manipulate URL query parameters

[hyperlink] provides methods for manipulating URL query parameters, which is how I manage bits of state.

The [hyperlink docs][hl_docs] have lots of examples, so start by reading those.

[hyperlink]: https://pypi.org/project/hyperlink/
[hl_docs]: https://hyperlink.readthedocs.io/en/latest/design.html#query-parameters



### Include the filename, content-type and content-length in a python-requests upload

When you upload a file through an HTML form:

```html
<form action="/upload" method="post" enctype="multipart/form-data">
  <input name="file" type="file">
  ...
</form>
```

it gets sent to the server with a filename, content-type and content-length (along with the contents, of course).

You can pass optional content-type and filename when uploading a file with requests by passing a 2-tuple or 3-tuple in the `files` list.
Two examples:

```python
import requests

requests.post(
    "/upload",
    files={"file": ("mydocument.pdf", open("mydocument.pdf", "rb"))},
)

requests.post(
    "/upload",
    files={"file": ("mydocument.pdf", open("mydocument.pdf", "rb"), "application/pdf")},
)
```

Relevant docs: <https://2.python-requests.org/en/master/api/#requests.request>




## Everything else

### Getting the cover image of an epub file

The preview-generator library doesn't have support for epub files, so I have to create thumbnails for those separately.
The first step is to get the cover image of the book.

I found some useful code for doing this on GitHub: <https://github.com/marianosimone/epub-thumbnailer> (GPL)

The basic gist:

*   An epub is a zip file, so look inside the zipfile and assume the biggest image entry is the cover image
*   Poke around inside the `container.xml` inside the epub

I'm using just the first approach for now, but the second might be useful if I ever have to store an image-heavy file.

The code in the GitHub repo is Python, but is fairly simple and could be ported to another language if necessary.



