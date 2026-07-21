"""Output processing and validation for RedundancyAI."""

import re
from typing import Optional
from langchain.schema import Document

from src.logger import setup_logger

logger = setup_logger(__name__)


class OutputProcessor:
    """Extract, validate, and format LLM output with citation verification."""

    # Pattern to match [Source: SourceName] citations
    CITATION_PATTERN = r"\[Source:\s*([^\]]+)\]"

    @staticmethod
    def extract_citations(answer_text: str) -> list[str]:
        """
        Extract all source citations from answer text.

        Args:
            answer_text: The LLM-generated answer

        Returns:
            List of cited source names (e.g., ["FWO_Redundancy_Pay", "NES_Summary"])
        """
        citations = re.findall(OutputProcessor.CITATION_PATTERN, answer_text)
        # Clean up whitespace
        citations = [c.strip() for c in citations]
        return citations

    @staticmethod
    def validate_citations(
        answer_text: str, retrieved_chunks: list[Document]
    ) -> dict:
        """
        Validate that all citations in answer match retrieved chunks.

        Args:
            answer_text: The LLM-generated answer
            retrieved_chunks: List of chunks returned from retrieval

        Returns:
            Validation result dict with:
                - valid: bool (all citations match)
                - cited_sources: list of sources mentioned in answer
                - retrieved_sources: list of sources in retrieved chunks
                - invalid_citations: list of citations not in retrieved chunks
        """
        # Extract citations from answer
        cited_sources = OutputProcessor.extract_citations(answer_text)

        # Get sources from retrieved chunks
        retrieved_sources = [
            chunk.metadata.get("source_name")
            for chunk in retrieved_chunks
            if chunk.metadata.get("source_name")
        ]
        retrieved_sources = list(set(retrieved_sources))  # Unique sources

        # Check: are all cited sources in retrieved sources?
        invalid_citations = []
        for source in cited_sources:
            if source not in retrieved_sources:
                invalid_citations.append(source)
                logger.warning(f"  ⚠ Citation '{source}' not found in retrieved chunks")

        validation_result = {
            "valid": len(invalid_citations) == 0,
            "cited_sources": cited_sources,
            "retrieved_sources": retrieved_sources,
            "invalid_citations": invalid_citations,
            "hallucination_detected": len(invalid_citations) > 0,
        }

        if validation_result["valid"]:
            logger.info(f"✓ Citations validated ({len(cited_sources)} citations match sources)")
        else:
            logger.warning(f"⚠ Hallucinated citations detected: {invalid_citations}")

        return validation_result

    @staticmethod
    def format_response(
        answer: str,
        retrieved_chunks: list[Document],
        confidence: float,
        validation_result: dict,
    ) -> dict:
        """
        Format response into structured output.

        Args:
            answer: The LLM-generated answer text
            retrieved_chunks: List of retrieved chunks used
            confidence: Confidence score (0-1)
            validation_result: Citation validation results

        Returns:
            Structured response dict
        """
        # Extract unique sources with metadata
        sources = []
        seen_sources = set()

        for chunk in retrieved_chunks:
            source_name = chunk.metadata.get("source_name")
            if source_name and source_name not in seen_sources:
                sources.append({
                    "name": source_name,
                    "doc_type": chunk.metadata.get("doc_type", "unknown"),
                    "url": chunk.metadata.get("url", ""),
                })
                seen_sources.add(source_name)

        response = {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "hallucination_detected": validation_result["hallucination_detected"],
            "cited_sources": validation_result["cited_sources"],
            "validation": {
                "citations_valid": validation_result["valid"],
                "invalid_citations": validation_result["invalid_citations"],
            },
        }

        return response

    @staticmethod
    def check_for_unsourced_claims(answer_text: str) -> dict:
        """
        Check for factual claims that lack citations.

        This is a heuristic check - looks for sentences with numbers/dates that might
        be facts but lack [Source: ...] tags.

        Args:
            answer_text: The LLM-generated answer

        Returns:
            Check result dict
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', answer_text)

        unsourced_facts = []
        for sentence in sentences:
            # Look for facts (contains numbers, percentages, dates)
            has_fact_indicators = any(
                indicator in sentence
                for indicator in ["%", "week", "year", "day", "$", "dollar"]
            )

            # Check if sentence has a citation
            has_citation = "[Source:" in sentence

            if has_fact_indicators and not has_citation:
                unsourced_facts.append(sentence.strip())

        return {
            "has_unsourced_claims": len(unsourced_facts) > 0,
            "unsourced_facts": unsourced_facts,
        }
