from docstore.merging import get_title_candidates, get_union_of_tags
from docstore.models import Document


class TestGetTitleCandidates:
    def test_single_document_is_title(self) -> None:
        doc = Document(title="Title 1")
        assert get_title_candidates([doc]) == ["Title 1"]

    def test_multiples_document_are_title_and_common_prefix(self) -> None:
        doc1 = Document(title="My document 1")
        doc2 = Document(title="My document 2")
        assert get_title_candidates([doc1, doc2]) == [
            "My document",
            "My document 1",
            "My document 2",
        ]

    def test_does_not_double_add_common_prefix(self) -> None:
        doc1 = Document(title="My document")
        doc2 = Document(title="My document 2")
        assert get_title_candidates([doc1, doc2]) == ["My document", "My document 2"]

    def test_does_not_double_add_title(self) -> None:
        doc1 = Document(title="My document")
        doc2 = Document(title="My document")
        assert get_title_candidates([doc1, doc2]) == ["My document"]

    def test_does_not_add_empty_prefix(self) -> None:
        doc1 = Document(title="My document")
        doc2 = Document(title="Another document")
        assert get_title_candidates([doc1, doc2]) == ["My document", "Another document"]


class TestGetUnionOfTags:
    def create_document_with_tags(self, tags: list[str]) -> Document:
        return Document(title="A test document", tags=tags)

    def test_tags_on_one_document_are_tags(self) -> None:
        doc = self.create_document_with_tags(tags=["tag1", "tag2", "tag3"])
        assert get_union_of_tags([doc]) == ["tag1", "tag2", "tag3"]

    def test_get_tags_on_multiple_documents_with_no_overlap(self) -> None:
        doc1 = self.create_document_with_tags(tags=["tag1"])
        doc2 = self.create_document_with_tags(tags=["tag2"])
        doc3 = self.create_document_with_tags(tags=["tag3"])
        assert get_union_of_tags([doc1, doc2, doc3]) == ["tag1", "tag2", "tag3"]

    def test_union_tags_deduplicates(self) -> None:
        doc1 = self.create_document_with_tags(tags=["tag1", "tag2"])
        doc2 = self.create_document_with_tags(tags=["tag3", "tag2"])
        doc3 = self.create_document_with_tags(tags=["tag3"])
        assert get_union_of_tags([doc1, doc2, doc3]) == ["tag1", "tag2", "tag3"]
