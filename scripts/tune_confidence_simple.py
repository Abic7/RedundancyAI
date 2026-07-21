"""Phase 6 (Simplified): Set confidence thresholds based on retrieval quality."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embed_store import VectorStoreManager
from src.config import CHROMA_PERSIST_DIR
from src.logger import setup_logger

logger = setup_logger(__name__)


# Test queries for threshold calibration (retrieval only, no LLM needed)
CALIBRATION_QUERIES = [
    # In-scope questions (should have high retrieval similarity)
    {
        "query": "How much redundancy pay after 4 years?",
        "should_match": True,
        "label": "In-scope: redundancy pay",
    },
    {
        "query": "What is the notice period for redundancy?",
        "should_match": True,
        "label": "In-scope: notice period",
    },
    {
        "query": "Annual leave entitlements calculation",
        "should_match": True,
        "label": "In-scope: leave calculation",
    },
    {
        "query": "Am I eligible for redundancy?",
        "should_match": True,
        "label": "In-scope: eligibility",
    },
    {
        "query": "Long service leave",
        "should_match": True,
        "label": "In-scope: long service leave",
    },
    {
        "query": "Unpaid entitlements on termination",
        "should_match": True,
        "label": "In-scope: unpaid entitlements",
    },
    {
        "query": "Modern award minimum rates",
        "should_match": True,
        "label": "In-scope: award rates",
    },
    {
        "query": "Part-time redundancy",
        "should_match": True,
        "label": "In-scope: part-time",
    },
    # Out-of-scope questions (should have low retrieval similarity)
    {
        "query": "What is the capital of France?",
        "should_match": False,
        "label": "Out-of-scope: geography",
    },
    {
        "query": "How do I claim unfair dismissal?",
        "should_match": False,
        "label": "Out-of-scope: unfair dismissal",
    },
]


def calibrate_thresholds():
    """Calibrate confidence thresholds based on retrieval similarity."""
    logger.info("╔════════════════════════════════════════════════════════════════╗")
    logger.info("║     PHASE 6: CONFIDENCE THRESHOLD CALIBRATION (RETRIEVAL)       ║")
    logger.info("╚════════════════════════════════════════════════════════════════╝")
    logger.info("")

    # Load vector store
    logger.info("Loading vector store...")
    manager = VectorStoreManager()
    vectorstore = manager.load_vectorstore(CHROMA_PERSIST_DIR)
    logger.info("✓ Vector store loaded")
    logger.info("")

    # Retrieve and score queries
    logger.info("Calibrating thresholds on retrieval similarity...")
    logger.info("")

    in_scope_scores = []
    out_of_scope_scores = []

    for test in CALIBRATION_QUERIES:
        query = test["query"]
        should_match = test["should_match"]
        label = test["label"]

        # Retrieve top-3
        chunks = vectorstore.similarity_search_with_score(query, k=3)

        # Get max similarity
        if chunks:
            max_similarity = chunks[0][1]  # (doc, score)
        else:
            max_similarity = 0.0

        if should_match:
            in_scope_scores.append(max_similarity)
            status = "✓"
        else:
            out_of_scope_scores.append(max_similarity)
            status = "✗"

        logger.info(f"{status} {label:<35} sim={max_similarity:.3f}")

    logger.info("")

    # Calculate statistics
    if in_scope_scores:
        in_scope_min = min(in_scope_scores)
        in_scope_avg = sum(in_scope_scores) / len(in_scope_scores)
        in_scope_max = max(in_scope_scores)
    else:
        in_scope_min = in_scope_avg = in_scope_max = 0.0

    if out_of_scope_scores:
        out_of_scope_min = min(out_of_scope_scores)
        out_of_scope_avg = sum(out_of_scope_scores) / len(out_of_scope_scores)
        out_of_scope_max = max(out_of_scope_scores)
    else:
        out_of_scope_min = out_of_scope_avg = out_of_scope_max = 0.0

    logger.info("Similarity Distribution:")
    logger.info("")
    logger.info("In-Scope Questions:")
    logger.info(f"  Min:  {in_scope_min:.3f}")
    logger.info(f"  Avg:  {in_scope_avg:.3f}")
    logger.info(f"  Max:  {in_scope_max:.3f}")
    logger.info("")
    logger.info("Out-of-Scope Questions:")
    logger.info(f"  Min:  {out_of_scope_min:.3f}")
    logger.info(f"  Avg:  {out_of_scope_avg:.3f}")
    logger.info(f"  Max:  {out_of_scope_max:.3f}")
    logger.info("")

    # Recommend threshold
    # Set to slightly above max out-of-scope to reject false positives
    recommended_threshold = round(min(out_of_scope_max + 0.05, in_scope_min - 0.05), 2)
    recommended_threshold = max(0.2, min(0.8, recommended_threshold))  # Clamp to [0.2, 0.8]

    logger.info("╔════════════════════════════════════════════════════════════════╗")
    logger.info("║             RECOMMENDED CONFIDENCE THRESHOLD                   ║")
    logger.info("╚════════════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info(f"Recommended Threshold: {recommended_threshold:.3f}")
    logger.info("")
    logger.info(f"Rationale:")
    logger.info(f"  • Reject queries with similarity < {recommended_threshold:.3f}")
    logger.info(f"  • Accept queries with similarity ≥ {recommended_threshold:.3f}")
    logger.info(f"  • Out-of-scope max: {out_of_scope_max:.3f}")
    logger.info(f"  • In-scope min: {in_scope_min:.3f}")
    logger.info("")

    # Save configuration
    config_data = {
        "confidence_threshold": float(recommended_threshold),
        "calibration_date": "2026-07-21",
        "in_scope": {
            "min": float(in_scope_min),
            "avg": float(in_scope_avg),
            "max": float(in_scope_max),
            "count": len(in_scope_scores),
        },
        "out_of_scope": {
            "min": float(out_of_scope_min),
            "avg": float(out_of_scope_avg),
            "max": float(out_of_scope_max),
            "count": len(out_of_scope_scores),
        },
    }

    output_file = Path(__file__).parent.parent / "data" / "confidence_calibration.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(config_data, f, indent=2)

    logger.info(f"Calibration saved to {output_file}")
    logger.info("")

    logger.info("╔════════════════════════════════════════════════════════════════╗")
    logger.info("║         ✅ PHASE 6 COMPLETE - THRESHOLD CALIBRATED             ║")
    logger.info("╚════════════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info(f"Next: Update config: CONFIDENCE_THRESHOLD = {recommended_threshold:.3f}")
    logger.info("Then: Phase 7 - Streamlit UI")

    return 0


if __name__ == "__main__":
    sys.exit(calibrate_thresholds())
