"""Retrieval quality audit - Phase 4.5."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embed_store import VectorStoreManager
from src.config import CHROMA_PERSIST_DIR
from src.logger import setup_logger

logger = setup_logger(__name__)


# Test queries with expected sources
TEST_QUERIES = [
    {
        "query": "How much redundancy pay after 4 years?",
        "expected_sources": ["FWO_Redundancy_Pay"],
        "should_be_relevant": True,
    },
    {
        "query": "What's the notice period for redundancy?",
        "expected_sources": ["NES_Summary"],
        "should_be_relevant": True,
    },
    {
        "query": "Annual leave entitlements",
        "expected_sources": ["FWO_Unpaid_Entitlements"],
        "should_be_relevant": True,
    },
    {
        "query": "Who is eligible for redundancy pay?",
        "expected_sources": ["FWA_Section_122", "NES_Summary"],
        "should_be_relevant": True,
    },
    {
        "query": "Long service leave calculation",
        "expected_sources": ["FWO_Unpaid_Entitlements"],
        "should_be_relevant": True,
    },
    {
        "query": "Part-time redundancy pay",
        "expected_sources": ["FWO_Redundancy_Pay"],
        "should_be_relevant": True,
    },
    {
        "query": "Modern award minimum pay",
        "expected_sources": ["Awards_Summary"],
        "should_be_relevant": True,
    },
    {
        "query": "Unpaid leave on termination",
        "expected_sources": ["FWO_Unpaid_Entitlements"],
        "should_be_relevant": True,
    },
    {
        "query": "What's the capital of France?",
        "expected_sources": [],
        "should_be_relevant": False,
    },
    {
        "query": "How do I claim unfair dismissal?",
        "expected_sources": [],
        "should_be_relevant": False,
    },
]


def is_chunk_relevant(chunk_text: str, query: str) -> bool:
    """
    Simple relevance check: does chunk contain key terms from query?

    In a real system, this would be manual human review.
    For now, we check for keyword overlap.
    """
    query_terms = set(query.lower().split())
    chunk_terms = set(chunk_text.lower().split())
    overlap = query_terms & chunk_terms

    # Need meaningful overlap (more than stop words)
    stop_words = {"the", "a", "an", "and", "or", "is", "of", "to", "for", "in"}
    meaningful_overlap = len(overlap - stop_words) >= 1

    return meaningful_overlap


def audit_retrieval():
    """Run retrieval quality audit."""
    logger.info("=== PHASE 4.5: RETRIEVAL QUALITY AUDIT ===")
    logger.info("")

    # Load vector store
    logger.info("Loading vector store...")
    manager = VectorStoreManager()
    vectorstore = manager.load_vectorstore(CHROMA_PERSIST_DIR)
    logger.info("✓ Vector store loaded")
    logger.info("")

    results = []
    passed = 0
    failed = 0

    for i, test in enumerate(TEST_QUERIES, 1):
        query = test["query"]
        expected_sources = test["expected_sources"]
        should_be_relevant = test["should_be_relevant"]

        logger.info(f"Test {i}/10: '{query}'")

        # Retrieve top-3 chunks
        chunks = vectorstore.similarity_search(query, k=3)
        retrieved_sources = list(set(c.metadata.get("source_name") for c in chunks))

        # Check relevance
        relevant_chunks = sum(1 for c in chunks if is_chunk_relevant(c.page_content, query))
        relevance_rate = relevant_chunks / len(chunks) if chunks else 0

        # Determine pass/fail
        if should_be_relevant:
            # For in-scope questions: need 2+ relevant chunks
            passed_test = relevant_chunks >= 2
            status = "✓ PASS" if passed_test else "✗ FAIL"
            if passed_test:
                passed += 1
            else:
                failed += 1
        else:
            # For out-of-scope questions: should have low relevance
            passed_test = relevant_chunks <= 1
            status = "✓ PASS (correctly rejected)" if passed_test else "✗ FAIL (false positive)"
            if passed_test:
                passed += 1
            else:
                failed += 1

        logger.info(f"  {status}")
        logger.info(f"  Relevant chunks: {relevant_chunks}/3 ({relevance_rate:.0%})")
        logger.info(f"  Retrieved sources: {retrieved_sources}")
        logger.info(f"  Top chunk: {chunks[0].page_content[:80]}...")
        logger.info("")

        results.append({
            "query": query,
            "should_be_relevant": should_be_relevant,
            "relevant_chunks": relevant_chunks,
            "relevance_rate": relevance_rate,
            "retrieved_sources": retrieved_sources,
            "passed": passed_test,
        })

    # Summary
    logger.info("=== AUDIT RESULTS ===")
    logger.info("")
    pass_rate = passed / len(TEST_QUERIES)
    logger.info(f"Pass rate: {passed}/{len(TEST_QUERIES)} ({pass_rate:.0%})")
    logger.info(f"Target: ≥90%")
    logger.info("")

    if pass_rate >= 0.90:
        logger.info("✅ RETRIEVAL QUALITY: PASS")
        logger.info("Proceeding to Phase 5 (RAG Chain)")
        return 0
    else:
        logger.info("❌ RETRIEVAL QUALITY: FAIL")
        logger.info("Issues detected:")
        for r in results:
            if not r["passed"]:
                logger.info(f"  • '{r['query']}' - {r['relevant_chunks']}/3 relevant")
        logger.info("")
        logger.info("Recommendations:")
        logger.info("  1. Check embedding model quality")
        logger.info("  2. Review chunk size (currently 700 words)")
        logger.info("  3. Consider document preprocessing (Phase 1.5)")
        return 1


if __name__ == "__main__":
    sys.exit(audit_retrieval())
