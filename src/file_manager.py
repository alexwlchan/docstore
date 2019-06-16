# -*- encoding: utf-8

import mimetypes
import pathlib
import tempfile

import attr
import magic

from thumbnails import create_thumbnail


@attr.s
class FileManager:
    root = attr.ib()

    # Whitenoise drops a warning if you initialise it against a non-existent
    # directory, so create it just to be sure.
    def __attrs_post_init__(self):
        self.root.mkdir(exist_ok=True, parents=True)

    def _store_file(self, file_id, original_file):
        file_identifier = pathlib.Path(file_id[0]) / (file_id + original_file.suffix)

        complete_file_identifier = self.root / file_identifier
        complete_file_identifier.parent.mkdir(exist_ok=True)
        original_file.rename(complete_file_identifier)

        return file_identifier

    def write_bytes(self, file_id, buffer, original_filename=None):
        if original_filename is not None:
            extension = pathlib.Path(original_filename).suffix
        else:
            # If we didn't get a filename from the user, try to guess one based
            # on the data.  Note that mimetypes will suggest ".jpe" for JPEG images,
            # so replace it with the more common extension by hand.
            assert isinstance(buffer, bytes)
            guessed_mimetype = magic.from_buffer(buffer, mime=True)
            if guessed_mimetype == "image/jpeg":
                extension = ".jpg"
            else:
                extension = mimetypes.guess_extension(guessed_mimetype)

        if extension is None:
            extension = ""

        _, tmp_path = tempfile.mkstemp(suffix=extension)
        tmp_path = pathlib.Path(tmp_path)
        tmp_path.write_bytes(buffer)

        return self._store_file(file_id, tmp_path)


class ThumbnailManager(FileManager):

    def create_thumbnail(self, file_id, original_file):
        thumbnail_path = create_thumbnail(original_file)
        return self._store_file(file_id, thumbnail_path)
