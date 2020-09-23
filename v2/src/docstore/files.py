import hashlib
import os
import re

from unidecode import unidecode

from docstore.models import Document, File, Thumbnail, from_json, to_json
from docstore.thumbnails import create_thumbnail


def get_documents(root):
    db_path = os.path.join(root, 'documents.json')

    try:
        with open(db_path) as infile:
            return from_json(infile.read())
    except FileNotFoundError:
        return []


def write_documents(*, root, documents):
    db_path = os.path.join(root, 'documents.json')
    json_string = to_json(documents)
    with open(db_path, 'w') as out_file:
        out_file.write(json_string)


def slugify(u):
    """
    Convert Unicode string into blog slug.

    Based on http://www.leancrew.com/all-this/2014/10/asciifying/

    """
    u = re.sub(u'[–—/:;,._]', '-', u)   # replace separating punctuation
    a = unidecode(u).lower()            # best ASCII substitutions, lowercased
    a = re.sub(r'[^a-z0-9 -]', '', a)   # delete any other characters
    a = a.replace(' ', '-')             # spaces to hyphens
    a = re.sub(r'-+', '-', a)           # condense repeated hyphens
    return a


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as infile:
        h.update(infile.read())

    return 'sha256:%s' % h.hexdigest()


def store_new_document(*, root, path, title, tags, date_created):
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    slug = slugify(name) + ext

    out_path = os.path.join('files', slug[0], slug)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    assert not os.path.exists(out_path)
    os.rename(path, out_path)

    thumbnail_path = create_thumbnail(out_path)
    thumbnail_name = os.path.basename(thumbnail_path)
    thumb_out_path = os.path.join('thumbnails', thumbnail_name[0], thumbnail_name)
    os.makedirs(os.path.dirname(thumb_out_path), exist_ok=True)
    os.rename(thumbnail_path, thumb_out_path)

    documents = get_documents(root)
    documents.append(
        Document(
            title=title,
            date_created=date_created,
            tags=tags,
            files=[
                File(
                    filename=filename,
                    path=out_path,
                    size=os.stat(out_path).st_size,
                    checksum=_sha256(out_path),
                    thumbnail=Thumbnail(thumb_out_path)
                )
            ]
        )
    )

    write_documents(root=root, documents=documents)
