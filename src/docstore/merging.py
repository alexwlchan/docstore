from .models import Document
from .text_utils import common_prefix


def get_title_candidates(documents: list[Document]) -> list[str]:
    title_candidates = []

    for doc in documents:
        if doc.title not in title_candidates:
            title_candidates.append(doc.title)

    guessed_title = common_prefix(title_candidates)

    if guessed_title and guessed_title not in title_candidates:
        title_candidates.insert(0, guessed_title)

    return title_candidates


def get_union_of_tags(documents: list[Document]) -> list[str]:
    """
    Get a list of every tag on any document in ``documents``.
    """
    tags = []

    for doc in documents:
        for t in doc.tags:
            if t not in tags:
                tags.append(t)

    return tags
