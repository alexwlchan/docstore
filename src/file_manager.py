# -*- encoding: utf-8

import mimetypes
import pathlib

import attr
import magic

from thumbnails import create_thumbnail


@attr.s
class FileManager:
    root = attr.ib()

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

        file_identifier = pathlib.Path(file_id[0]) / (file_id + extension)

        complete_file_identifier = self.root / file_identifier
        complete_file_identifier.parent.mkdir(exist_ok=True, parents=True)
        complete_file_identifier.write_bytes(buffer)

        return file_identifier


class ThumbnailManager(FileManager):

    def create_thumbnail(self, file_id, original_file):
        thumbnail = create_thumbnail(original_file)
        return self.write_bytes(
            file_id=file_id,
            buffer=thumbnail.read_bytes(),
            original_filename=thumbnail
        )
