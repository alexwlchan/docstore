from docstore.merging import get_title_candidates
from docstore.models import Document


def create_document_with(*, title):
    return Document(title=title)


class TestGetTitleCandidates:
    def test_single_document_is_title(self):
        doc = Document(title="Title 1")
        assert get_title_candidates([doc]) == ["Title 1"]

    def test_multiples_document_are_title_and_common_prefix(self):
        doc1 = Document(title="My document 1")
        doc2 = Document(title="My document 2")
        assert get_title_candidates([doc1, doc2]) == [
            "My document",
            "My document 1",
            "My document 2",
        ]

    def test_does_not_double_add_common_prefix(self):
        doc1 = Document(title="My document")
        doc2 = Document(title="My document 2")
        assert get_title_candidates([doc1, doc2]) == ["My document", "My document 2"]

    def test_does_not_double_add_title(self):
        doc1 = Document(title="My document")
        doc2 = Document(title="My document")
        assert get_title_candidates([doc1, doc2]) == ["My document"]

    def test_does_not_add_empty_prefix(self):
        doc1 = Document(title="My document")
        doc2 = Document(title="Another document")
        assert get_title_candidates([doc1, doc2]) == ["My document", "Another document"]
