"""Download Fair Work source documents for RedundancyAI."""

import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import RAW_DATA_DIR
from src.logger import setup_logger

logger = setup_logger(__name__)

# Document registry with download URLs
DOCUMENTS = {
    "FWO_Redundancy_Pay": {
        "filename": "fwo_redundancy_pay.pdf",
        "url": "https://www.fairwork.gov.au/documents-and-publications/fact-sheets-and-templates/fact-sheets/minimum-wages-and-conditions/redundancy-pay",
        "doc_type": "factsheet",
        "size_hint_kb": 500,
    },
    "NES_Summary": {
        "filename": "nes_summary.pdf",
        "url": "https://www.fairwork.gov.au/workplace-rights/national-employment-standards",
        "doc_type": "guide",
        "size_hint_kb": 300,
    },
    "FWA_Section_122": {
        "filename": "fair_work_act_excerpt.txt",
        "url": "https://www.legislation.gov.au/C2009A00001/latest/text",
        "doc_type": "legislation",
        "size_hint_kb": 50,
    },
    "FWO_Unpaid_Entitlements": {
        "filename": "unpaid_entitlements.pdf",
        "url": "https://www.fairwork.gov.au/documents-and-publications/fact-sheets-and-templates/fact-sheets/entitlements/unpaid-entitlements",
        "doc_type": "guide",
        "size_hint_kb": 300,
    },
    "Awards_Summary": {
        "filename": "awards_summary.csv",
        "url": "https://www.fairwork.gov.au/awards-and-agreements/awards",
        "doc_type": "reference",
        "size_hint_kb": 100,
    },
}


def get_session_with_retries(retries: int = 3, timeout: int = 10) -> requests.Session:
    """
    Create a requests session with retry logic.

    Args:
        retries: Number of retries
        timeout: Timeout in seconds

    Returns:
        Configured requests.Session
    """
    session = requests.Session()
    retry = Retry(total=retries, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def compute_checksum(filepath: Path) -> str:
    """
    Compute SHA-256 checksum of a file.

    Args:
        filepath: Path to file

    Returns:
        SHA-256 hex digest
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def download_document(
    source_name: str, doc_info: dict, output_dir: Path, session: requests.Session
) -> Optional[dict]:
    """
    Download a single Fair Work document.

    Args:
        source_name: Identifier (e.g., "FWO_Redundancy_Pay")
        doc_info: Document metadata dict
        output_dir: Where to save the file
        session: Requests session with retry logic

    Returns:
        Download result dict or None if failed
    """
    filename = doc_info["filename"]
    url = doc_info["url"]
    doc_type = doc_info["doc_type"]

    filepath = output_dir / filename

    # Check if already exists
    if filepath.exists():
        logger.info(f"✓ {filename} already exists, skipping")
        checksum = compute_checksum(filepath)
        return {
            "source_name": source_name,
            "filename": filename,
            "status": "skipped",
            "checksum": checksum,
            "downloaded_at": None,
        }

    logger.info(f"Downloading: {filename} from {source_name}")
    logger.info(f"  URL: {url}")

    try:
        response = session.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()

        # Save file
        filepath.write_bytes(response.content)

        # Validate size
        file_size_kb = filepath.stat().st_size / 1024
        logger.info(f"  Size: {file_size_kb:.1f} KB")

        if file_size_kb < 10:
            logger.warning(f"  ⚠ File suspiciously small (<10 KB), may be error page")

        # Compute checksum
        checksum = compute_checksum(filepath)
        logger.info(f"  Checksum: {checksum[:16]}...")

        return {
            "source_name": source_name,
            "filename": filename,
            "status": "downloaded",
            "checksum": checksum,
            "size_kb": file_size_kb,
            "downloaded_at": datetime.now().isoformat(),
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"  ✗ Failed: {e}")
        return {
            "source_name": source_name,
            "filename": filename,
            "status": "failed",
            "error": str(e),
        }


def main():
    """Download all Fair Work source documents."""
    logger.info("=== RedundancyAI Document Downloader ===")
    logger.info("")

    # Ensure output directory exists
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Create session with retries
    session = get_session_with_retries()

    # Download all documents
    results = []
    for source_name, doc_info in DOCUMENTS.items():
        result = download_document(source_name, doc_info, RAW_DATA_DIR, session)
        if result:
            results.append(result)

    session.close()

    # Summary
    logger.info("")
    logger.info("=== Download Summary ===")
    downloaded = sum(1 for r in results if r["status"] == "downloaded")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "failed")

    logger.info(f"Downloaded: {downloaded}")
    logger.info(f"Skipped (existing): {skipped}")
    logger.info(f"Failed: {failed}")

    if failed > 0:
        logger.warning("")
        logger.warning("⚠ Some documents failed to download:")
        for result in results:
            if result["status"] == "failed":
                logger.warning(f"  - {result['filename']}: {result.get('error', 'Unknown error')}")

    # Save results
    results_file = RAW_DATA_DIR / "download_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to: {results_file}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
