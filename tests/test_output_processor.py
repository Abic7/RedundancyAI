"""Tests for output processor and citation validation."""

import pytest
from langchain.schema import Document
from src.output_processor import OutputProcessor


class TestCitationExtraction:
    """Test citation extraction from answer text."""

    def test_extract_single_citation(self):
        """Extract single citation from answer."""
        answer = "Redundancy pay is 4 weeks [Source: FWO_Redundancy_Pay]."
        citations = OutputProcessor.extract_citations(answer)
        assert citations == ["FWO_Redundancy_Pay"]

    def test_extract_multiple_citations(self):
        """Extract multiple citations from answer."""
        answer = "Pay is 4 weeks [Source: FWO_Redundancy_Pay] plus 1 week per year [Source: NES_Summary]."
        citations = OutputProcessor.extract_citations(answer)
        assert set(citations) == {"FWO_Redundancy_Pay", "NES_Summary"}

    def test_extract_no_citations(self):
        """No citations in answer."""
        answer = "This answer has no citations."
        citations = OutputProcessor.extract_citations(answer)
        assert citations == []

    def test_extract_with_whitespace(self):
        """Handle whitespace in citation tags."""
        answer = "Answer [Source:  FWO_Redundancy_Pay  ] here."
        citations = OutputProcessor.extract_citations(answer)
        assert citations == ["FWO_Redundancy_Pay"]


class TestCitationValidation:
    """Test citation validation against retrieved chunks."""

    def test_valid_citations(self):
        """All citations match retrieved chunks."""
        answer = "Pay is 4 weeks [Source: FWO_Redundancy_Pay] and notice is required [Source: NES_Summary]."
        chunks = [
            Document(
                page_content="Redundancy pay is 4 weeks...",
                metadata={"source_name": "FWO_Redundancy_Pay", "doc_type": "factsheet"}
            ),
            Document(
                page_content="Notice period is...",
                metadata={"source_name": "NES_Summary", "doc_type": "guide"}
            ),
        ]

        result = OutputProcessor.validate_citations(answer, chunks)
        assert result["valid"] is True
        assert result["invalid_citations"] == []

    def test_invalid_citations_hallucinated(self):
        """Detect hallucinated citations."""
        answer = "Answer [Source: Made_Up_Document]."
        chunks = [
            Document(
                page_content="Some content",
                metadata={"source_name": "FWO_Redundancy_Pay", "doc_type": "factsheet"}
            ),
        ]

        result = OutputProcessor.validate_citations(answer, chunks)
        assert result["valid"] is False
        assert "Made_Up_Document" in result["invalid_citations"]
        assert result["hallucination_detected"] is True

    def test_partial_hallucination(self):
        """Detect mixed valid and invalid citations."""
        answer = "Valid [Source: FWO_Redundancy_Pay] and invalid [Source: Fake_Source]."
        chunks = [
            Document(
                page_content="Content",
                metadata={"source_name": "FWO_Redundancy_Pay", "doc_type": "factsheet"}
            ),
        ]

        result = OutputProcessor.validate_citations(answer, chunks)
        assert result["valid"] is False
        assert "FWO_Redundancy_Pay" in result["cited_sources"]
        assert "Fake_Source" in result["invalid_citations"]


class TestUnsourcedClaims:
    """Test detection of factual claims without citations."""

    def test_detect_unsourced_fact(self):
        """Detect number/fact without citation."""
        answer = "Redundancy pay is 8 weeks. This is important [Source: FWO_Redundancy_Pay]."
        result = OutputProcessor.check_for_unsourced_claims(answer)
        # First sentence has "8 weeks" but no citation
        assert result["has_unsourced_claims"] is True

    def test_all_facts_sourced(self):
        """All facts have citations."""
        answer = "Redundancy pay is 8 weeks [Source: FWO_Redundancy_Pay]."
        result = OutputProcessor.check_for_unsourced_claims(answer)
        assert result["has_unsourced_claims"] is False

    def test_subjective_statements_ok(self):
        """Subjective statements don't need citations."""
        answer = "This is important information."
        result = OutputProcessor.check_for_unsourced_claims(answer)
        # No numbers/facts, so no unsourced claims
        assert result["has_unsourced_claims"] is False


class TestResponseFormatting:
    """Test structured response formatting."""

    def test_format_response(self):
        """Format complete response with all fields."""
        answer = "Redundancy pay is 4 weeks [Source: FWO_Redundancy_Pay]."
        chunks = [
            Document(
                page_content="Redundancy pay...",
                metadata={
                    "source_name": "FWO_Redundancy_Pay",
                    "doc_type": "factsheet",
                    "url": "https://example.com/fwo"
                }
            ),
        ]
        validation = {
            "valid": True,
            "cited_sources": ["FWO_Redundancy_Pay"],
            "invalid_citations": [],
            "hallucination_detected": False,
        }

        response = OutputProcessor.format_response(answer, chunks, 0.92, validation)

        assert response["answer"] == answer
        assert response["confidence"] == 0.92
        assert response["hallucination_detected"] is False
        assert len(response["sources"]) == 1
        assert response["sources"][0]["name"] == "FWO_Redundancy_Pay"

    def test_format_response_with_refusal(self):
        """Format refusal response."""
        answer = "I don't have reliable information about that."
        chunks = []
        validation = {
            "valid": True,
            "cited_sources": [],
            "invalid_citations": [],
            "hallucination_detected": False,
        }

        response = OutputProcessor.format_response(answer, chunks, 0.2, validation)

        assert response["confidence"] == 0.2
        assert len(response["sources"]) == 0
