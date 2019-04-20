# What I learnt

The point of this project was to play with some new tools (responder, Bootstrap, more JavaScript).
I've learnt a bunch while doing the project, but it's hard to see it in one place.
There are inline comments that explain what a piece of code is doing, but they're scattered around the codebase.

For my benefit and for everybody else, this file has a short list of some of the things I learnt while working on docstore.
I'll add to the file as I learn more!


## The Content-Disposition HTTP header

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


## The whitenoise library

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


## The python-magic library and the ".jpe" file extension

[python-magic] is a library for detecting the mimetype of some bytes.
A simple example:

```python
import magic

assert isinstance(data, bytes)
guessed_mimetype = magic.from_buffer(data, mime=True)
```

Then you can use the [mimetypes] library to get an appropriate filename extension:

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

[magic]: https://pypi.org/project/python-magic/
[mimetypes]: https://docs.python.org/3/library/mimetypes.html
[guess_extension]: https://github.com/python/cpython/blob/7e18deef652a9d413d5dbd19d61073ba7eb5460e/Lib/mimetypes.py#L179-L195
