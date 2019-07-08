# -*- encoding: utf-8

import errno
import mimetypes
import pathlib
import shutil
import tempfile

import attr
import magic

from file_writer import safe_write
from slugify import slugify
from thumbnails import create_thumbnail


@attr.s
class FileManager:
    root = attr.ib(converter=pathlib.Path)

    def write_bytes(self, file_id, buffer, original_filename=None):
        # Try to store the file with a human-readable filename if supplied.
        if original_filename is not None:
            pth = pathlib.Path(original_filename)
            base_name = slugify(pth.stem)

            if not base_name:
                base_name = file_id

            extension = pth.suffix
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
            base_name = file_id

        if extension is None:
            extension = ""

        shard = base_name[0].lower()
        file_identifier = pathlib.Path(shard) / (base_name + extension)

        out_path = self.root / file_identifier
        out_path.parent.mkdir(exist_ok=True, parents=True)

        out_file = safe_write(out_path, data=buffer)
        return out_file.relative_to(self.root)


class ThumbnailManager(FileManager):

    def _store_file(self, base_name, original_file):
        shard = base_name[0].lower()
        file_identifier = pathlib.Path(shard) / (base_name + original_file.suffix)

        complete_file_identifier = self.root / file_identifier
        complete_file_identifier.parent.mkdir(exist_ok=True, parents=True)

        # This can throw an error if we try to do a rename across devices;
        # in that case fall back to a non-atomic copy operation.
        try:
            original_file.rename(complete_file_identifier)
        except OSError as err:
            if err.errno == errno.EXDEV:
                shutil.copyfile(original_file, complete_file_identifier)
                original_file.unlink()
            else:  # pragma: no cover
                raise

        return file_identifier

    def create_thumbnail(self, file_id, original_file):
        thumbnail_path = create_thumbnail(original_file)
        return self._store_file(file_id, thumbnail_path)
