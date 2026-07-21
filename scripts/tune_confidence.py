"""Phase 6: Confidence threshold tuning - optimize F1 score."""

import sys
import json
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_chain import RAGChain
from src.logger import setup_logger

logger = setup_logger(__name__)


# Golden test set: questions with known answers + expected confidence
GOLDEN_TEST_SET = [
    {
        "question": "How much redundancy pay after 4 years?",
        "expected_answer_keywords": ["4 weeks", "7", "8"],
        "should_answer": True,
        "min_expected_confidence": 0.7,
    },
    {
        "question": "What's the notice period for redundancy?",
        "expected_answer_keywords": ["weeks", "notice"],
        "should_answer": True,
        "min_expected_confidence": 0.6,
    },
    {
        "question": "Annual leave entitlements",
        "expected_answer_keywords": ["leave", "year", "weeks"],
        "should_answer": True,
        "min_expected_confidence": 0.65,
    },
    {
        "question": "Who is eligible for redundancy pay?",
        "expected_answer_keywords": ["eligib", "years", "employ"],
        "should_answer": True,
        "min_expected_confidence": 0.6,
    },
    {
        "question": "Long service leave calculation",
        "expected_answer_keywords": ["service", "leave", "year"],
        "should_answer": True,
        "min_expected_confidence": 0.65,
    },
    {
        "question": "Part-time redundancy pay",
        "expected_answer_keywords": ["part", "redundancy", "pay"],
        "should_answer": True,
        "min_expected_confidence": 0.6,
    },
    {
        "question": "Modern award minimum pay",
        "expected_answer_keywords": ["award", "minimum", "pay"],
        "should_answer": True,
        "min_expected_confidence": 0.6,
    },
    {
        "question": "Unpaid leave on termination",
        "expected_answer_keywords": ["leave", "termination", "unpaid"],
        "should_answer": True,
        "min_expected_confidence": 0.65,
    },
    # Out-of-scope questions (should refuse)
    {
        "question": "What's the capital of France?",
        "expected_answer_keywords": [],
        "should_answer": False,
        "max_expected_confidence": 0.3,
    },
    {
        "question": "How do I claim unfair dismissal?",
        "expected_answer_keywords": [],
        "should_answer": False,
        "max_expected_confidence": 0.4,
    },
]


class ConfidenceThresholdTuner:
    """Tune confidence threshold to optimize F1 score."""

    def __init__(self, rag_chain: RAGChain):
        """Initialize tuner with RAG chain."""
        self.chain = rag_chain
        self.results = []

    def evaluate_threshold(self, threshold: float) -> dict:
        """
        Evaluate RAG chain at a specific confidence threshold.

        Returns:
            {
                "threshold": float,
                "precision": float,
                "recall": float,
                "f1": float,
                "accuracy": float,
                "true_positives": int,
                "false_positives": int,
                "true_negatives": int,
                "false_negatives": int,
                "results": [test results],
            }
        """
        logger.info(f"Evaluating threshold: {threshold:.3f}")

        tp = 0  # Correct refusal (low conf on out-of-scope)
        fp = 0  # Incorrect refusal (low conf on in-scope)
        tn = 0  # Correct answer (high conf on in-scope)
        fn = 0  # Hallucinated answer (high conf but wrong)

        test_results = []

        for i, test in enumerate(GOLDEN_TEST_SET, 1):
            question = test["question"]
            should_answer = test["should_answer"]

            # Query RAG chain
            response = self.chain.answer_question(question)
            confidence = response["confidence"]

            # Determine if system will answer at this threshold
            will_answer = confidence >= threshold

            # Determine if answer is correct
            answer_text = response["answer"].lower()
            has_relevant_keywords = any(
                kw.lower() in answer_text
                for kw in test.get("expected_answer_keywords", [])
            )
            is_correct = has_relevant_keywords if should_answer else True

            # Confusion matrix
            if should_answer:
                if will_answer and is_correct:
                    tp += 1
                    result_type = "TP"
                elif will_answer and not is_correct:
                    fn += 1
                    result_type = "FN"
                elif not will_answer:
                    fp += 1
                    result_type = "FP"
                else:
                    fn += 1
                    result_type = "FN"
            else:
                if not will_answer:
                    tn += 1
                    result_type = "TN"
                else:
                    fp += 1
                    result_type = "FP"

            test_results.append({
                "question": question[:50],
                "should_answer": should_answer,
                "confidence": confidence,
                "will_answer": will_answer,
                "is_correct": is_correct,
                "type": result_type,
            })

        # Calculate metrics
        total = len(GOLDEN_TEST_SET)
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "threshold": threshold,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "accuracy": accuracy,
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "results": test_results,
        }

    def tune(self, start: float = 0.2, end: float = 0.8, step: float = 0.05) -> dict:
        """
        Search for optimal threshold that maximizes F1 score.

        Returns:
            {
                "optimal_threshold": float,
                "optimal_f1": float,
                "optimal_metrics": dict,
                "all_thresholds": [evaluation results],
            }
        """
        logger.info("")
        logger.info("=== CONFIDENCE THRESHOLD TUNING ===")
        logger.info("")
        logger.info(f"Testing thresholds from {start:.2f} to {end:.2f} (step {step:.2f})")
        logger.info("")

        all_results = []
        best_f1 = 0.0
        best_threshold = start
        best_metrics = None

        # Test each threshold
        thresholds = [round(start + i * step, 2) for i in range(int((end - start) / step) + 1)]

        for threshold in thresholds:
            metrics = self.evaluate_threshold(threshold)
            all_results.append(metrics)

            f1 = metrics["f1"]
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold
                best_metrics = metrics

            # Log progress
            logger.info(f"  Threshold {threshold:.2f} → F1={f1:.3f} | P={metrics['precision']:.3f} R={metrics['recall']:.3f} Acc={metrics['accuracy']:.3f}")

        logger.info("")
        logger.info(f"✓ Tuning complete")
        logger.info("")

        return {
            "optimal_threshold": best_threshold,
            "optimal_f1": best_f1,
            "optimal_metrics": best_metrics,
            "all_thresholds": all_results,
        }


def print_threshold_analysis(tuning_result: dict):
    """Pretty-print threshold tuning results."""
    optimal = tuning_result["optimal_metrics"]

    logger.info("╔════════════════════════════════════════════════════════════════╗")
    logger.info("║        OPTIMAL CONFIDENCE THRESHOLD FOUND                      ║")
    logger.info("╚════════════════════════════════════════════════════════════════╝")
    logger.info("")

    logger.info(f"Optimal Threshold: {tuning_result['optimal_threshold']:.3f}")
    logger.info(f"Optimal F1 Score:  {tuning_result['optimal_f1']:.3f}")
    logger.info("")

    logger.info("Metrics at Optimal Threshold:")
    logger.info(f"  Precision: {optimal['precision']:.3f} (correct answers / total answers)")
    logger.info(f"  Recall:    {optimal['recall']:.3f} (answered correctly / should answer)")
    logger.info(f"  Accuracy:  {optimal['accuracy']:.3f} (correct decisions / total)")
    logger.info("")

    logger.info("Confusion Matrix:")
    logger.info(f"  TP (correct answers):  {optimal['true_positives']}")
    logger.info(f"  TN (correct refusals): {optimal['true_negatives']}")
    logger.info(f"  FP (false refusals):   {optimal['false_positives']}")
    logger.info(f"  FN (hallucinations):   {optimal['false_negatives']}")
    logger.info("")

    # Show worst cases
    logger.info("Test Results at Optimal Threshold:")
    logger.info("")
    for result in optimal["results"]:
        symbol = "✓" if result["type"] in ["TP", "TN"] else "✗"
        logger.info(f"  {symbol} {result['type']} | {result['question'][:40]:<40} | conf={result['confidence']:.3f}")

    logger.info("")


def save_tuning_results(tuning_result: dict, output_file: Path):
    """Save tuning results to JSON file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert for JSON serialization
    data = {
        "optimal_threshold": tuning_result["optimal_threshold"],
        "optimal_f1": tuning_result["optimal_f1"],
        "optimal_metrics": {
            "threshold": tuning_result["optimal_metrics"]["threshold"],
            "precision": tuning_result["optimal_metrics"]["precision"],
            "recall": tuning_result["optimal_metrics"]["recall"],
            "f1": tuning_result["optimal_metrics"]["f1"],
            "accuracy": tuning_result["optimal_metrics"]["accuracy"],
            "true_positives": tuning_result["optimal_metrics"]["true_positives"],
            "false_positives": tuning_result["optimal_metrics"]["false_positives"],
            "true_negatives": tuning_result["optimal_metrics"]["true_negatives"],
            "false_negatives": tuning_result["optimal_metrics"]["false_negatives"],
        },
        "all_thresholds": [
            {
                "threshold": t["threshold"],
                "precision": t["precision"],
                "recall": t["recall"],
                "f1": t["f1"],
                "accuracy": t["accuracy"],
            }
            for t in tuning_result["all_thresholds"]
        ],
    }

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Results saved to {output_file}")


def main():
    """Run confidence threshold tuning."""
    logger.info("╔════════════════════════════════════════════════════════════════╗")
    logger.info("║        PHASE 6: CONFIDENCE THRESHOLD TUNING                     ║")
    logger.info("╚════════════════════════════════════════════════════════════════╝")
    logger.info("")

    try:
        # Initialize RAG chain
        logger.info("Initializing RAG chain...")
        chain = RAGChain()
        logger.info("✓ RAG chain initialized")
        logger.info("")

        # Run tuning
        tuner = ConfidenceThresholdTuner(chain)
        tuning_result = tuner.tune(start=0.2, end=0.8, step=0.05)

        # Print results
        print_threshold_analysis(tuning_result)

        # Save results
        output_file = Path(__file__).parent.parent / "data" / "tuning_results.json"
        save_tuning_results(tuning_result, output_file)

        logger.info("╔════════════════════════════════════════════════════════════════╗")
        logger.info("║        ✅ PHASE 6 COMPLETE - THRESHOLD TUNED                   ║")
        logger.info("╚════════════════════════════════════════════════════════════════╝")
        logger.info("")
        logger.info(f"Update config: CONFIDENCE_THRESHOLD={tuning_result['optimal_threshold']:.3f}")
        logger.info("Next: Phase 7 - Streamlit UI")

        return 0

    except Exception as e:
        logger.error(f"Tuning failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
