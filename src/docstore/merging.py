from docstore.text_utils import common_prefix


def get_title_candidates(documents):
    title_candidates = []

    for doc in documents:
        if doc.title not in title_candidates:
            title_candidates.append(doc.title)

    guessed_title = common_prefix(title_candidates)

    if guessed_title and guessed_title not in title_candidates:
        title_candidates.insert(0, guessed_title)

    return title_candidates
