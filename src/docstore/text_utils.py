import os
import re

from unidecode import unidecode


def common_prefix(values):
    prefix = os.path.commonprefix(values).strip()

    prefix = prefix.strip('()').strip()
    if prefix.lower().endswith('(part'):
        prefix = prefix[:-len('(part')].strip()

    if prefix.lower().endswith('- part'):
        prefix = prefix[:-len('- part')].strip()

    return prefix


def slugify(u):
    """
    Convert Unicode string into blog slug.

    Based on http://www.leancrew.com/all-this/2014/10/asciifying/

    """
    u = re.sub(u"[–—/:;,._]", "-", u)  # replace separating punctuation
    a = unidecode(u).lower()  # best ASCII substitutions, lowercased
    a = re.sub(r"[^a-z0-9 -]", "", a)  # delete any other characters
    a = a.replace(" ", "-")  # spaces to hyphens
    a = re.sub(r"-+", "-", a)  # condense repeated hyphens
    return a
