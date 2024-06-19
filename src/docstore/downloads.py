import cgi
from email.message import Message
import os
import pathlib
from urllib.request import urlretrieve
from urllib.parse import urlparse


def guess_filename(url: str, headers: Message) -> str:
    """
    Given a URL and the HTTP response headers, guess the final name of this file.
    """
    fallback = os.path.basename(urlparse(url).path)

    try:
        _, params = cgi.parse_header(headers["Content-Disposition"])
    except TypeError:
        return fallback

    try:
        return params["filename"]
    except (KeyError, TypeError):
        return fallback


def download_file(url: str) -> pathlib.Path:  # pragma: no cover
    """
    Download a file from a URL.  Returns the path to the downloaded file.
    """
    tmp_path, headers = urlretrieve(url)

    filename = guess_filename(url=url, headers=headers)

    out_path = os.path.join(os.path.dirname(tmp_path), filename)
    os.rename(tmp_path, out_path)

    return pathlib.Path(out_path)
