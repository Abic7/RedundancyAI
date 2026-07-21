"""Document ingestion pipeline for RedundancyAI."""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.config import CHUNK_SIZE, CHUNK_OVERLAP, RAW_DATA_DIR, SOURCES_REGISTRY_FILE
from src.logger import setup_logger

logger = setup_logger(__name__)


class DocumentIngestionPipeline:
    """Load, parse, and chunk Fair Work documents."""

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        """
        Initialize ingestion pipeline.

        Args:
            chunk_size: Size of text chunks (tokens/words)
            chunk_overlap: Overlap between chunks to preserve context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.source_metadata = self._load_source_registry()

    def _load_source_registry(self) -> dict:
        """Load source document registry from SOURCES.md."""
        # Hardcoded registry with support for both real and mock files
        registry = {
            "fwo_redundancy_pay.pdf": {
                "source_name": "FWO_Redundancy_Pay",
                "doc_type": "factsheet",
                "url": "https://www.fairwork.gov.au/documents-and-publications/fact-sheets-and-templates/fact-sheets/minimum-wages-and-conditions/redundancy-pay",
            },
            "fwo_redundancy_pay_mock.txt": {
                "source_name": "FWO_Redundancy_Pay",
                "doc_type": "factsheet",
                "url": "https://www.fairwork.gov.au/documents-and-publications/fact-sheets-and-templates/fact-sheets/minimum-wages-and-conditions/redundancy-pay",
            },
            "nes_summary.pdf": {
                "source_name": "NES_Summary",
                "doc_type": "guide",
                "url": "https://www.fairwork.gov.au/workplace-rights/national-employment-standards",
            },
            "nes_summary_mock.txt": {
                "source_name": "NES_Summary",
                "doc_type": "guide",
                "url": "https://www.fairwork.gov.au/workplace-rights/national-employment-standards",
            },
            "fair_work_act_excerpt.txt": {
                "source_name": "FWA_Section_122",
                "doc_type": "legislation",
                "url": "https://www.legislation.gov.au/C2009A00001/latest/text",
            },
            "unpaid_entitlements.pdf": {
                "source_name": "FWO_Unpaid_Entitlements",
                "doc_type": "guide",
                "url": "https://www.fairwork.gov.au/documents-and-publications/fact-sheets-and-templates/fact-sheets/entitlements/unpaid-entitlements",
            },
            "unpaid_entitlements_mock.txt": {
                "source_name": "FWO_Unpaid_Entitlements",
                "doc_type": "guide",
                "url": "https://www.fairwork.gov.au/documents-and-publications/fact-sheets-and-templates/fact-sheets/entitlements/unpaid-entitlements",
            },
            "awards_summary.csv": {
                "source_name": "Awards_Summary",
                "doc_type": "reference",
                "url": "https://www.fairwork.gov.au/awards-and-agreements/awards",
            },
        }
        return registry

    def load_documents(self, raw_dir: Optional[Path] = None) -> list[Document]:
        """
        Load documents from raw_dir (PDFs, TXT, CSV).

        Args:
            raw_dir: Directory containing raw documents

        Returns:
            List of Document objects with metadata
        """
        raw_dir = raw_dir or RAW_DATA_DIR
        documents = []

        logger.info(f"Loading documents from {raw_dir}")

        # Get all document files
        pdf_files = list(raw_dir.glob("*.pdf"))
        txt_files = list(raw_dir.glob("*.txt"))
        csv_files = list(raw_dir.glob("*.csv"))

        total_files = len(pdf_files) + len(txt_files) + len(csv_files)
        logger.info(f"Found {total_files} documents to process")

        # Load PDFs
        for pdf_file in pdf_files:
            try:
                logger.info(f"  Loading PDF: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()

                # Attach metadata
                for doc in docs:
                    metadata = self.source_metadata.get(pdf_file.name, {})
                    doc.metadata.update(metadata)
                    doc.metadata["file_type"] = "pdf"
                    doc.metadata["retrieved_at"] = datetime.now().isoformat()

                documents.extend(docs)
                logger.info(f"    ✓ Loaded {len(docs)} pages from {pdf_file.name}")

            except Exception as e:
                logger.error(f"    ✗ Failed to load {pdf_file.name}: {e}")

        # Load text files
        for txt_file in txt_files:
            try:
                logger.info(f"  Loading TXT: {txt_file.name}")
                loader = TextLoader(str(txt_file))
                docs = loader.load()

                # Attach metadata
                for doc in docs:
                    metadata = self.source_metadata.get(txt_file.name, {})
                    doc.metadata.update(metadata)
                    doc.metadata["file_type"] = "txt"
                    doc.metadata["retrieved_at"] = datetime.now().isoformat()

                documents.extend(docs)
                logger.info(f"    ✓ Loaded from {txt_file.name}")

            except Exception as e:
                logger.error(f"    ✗ Failed to load {txt_file.name}: {e}")

        # Load CSV files (as text)
        for csv_file in csv_files:
            try:
                logger.info(f"  Loading CSV: {csv_file.name}")
                with open(csv_file, "r", encoding="utf-8") as f:
                    content = f.read()

                doc = Document(page_content=content)
                metadata = self.source_metadata.get(csv_file.name, {})
                doc.metadata.update(metadata)
                doc.metadata["file_type"] = "csv"
                doc.metadata["retrieved_at"] = datetime.now().isoformat()

                documents.append(doc)
                logger.info(f"    ✓ Loaded from {csv_file.name}")

            except Exception as e:
                logger.error(f"    ✗ Failed to load {csv_file.name}: {e}")

        logger.info(f"Total documents loaded: {len(documents)}")
        return documents

    def chunk_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into chunks while preserving metadata.

        Args:
            documents: List of Document objects

        Returns:
            List of chunked Document objects with metadata
        """
        logger.info(f"Chunking {len(documents)} documents...")
        logger.info(f"  Chunk size: {self.chunk_size}, overlap: {self.chunk_overlap}")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

        chunks = []
        for doc in documents:
            doc_chunks = splitter.split_documents([doc])
            chunks.extend(doc_chunks)

        logger.info(f"Total chunks created: {len(chunks)}")
        return chunks

    def validate_chunks(self, chunks: list[Document]) -> dict:
        """
        Validate chunk quality (metadata, length, etc.).

        Args:
            chunks: List of chunked documents

        Returns:
            Validation report dictionary
        """
        logger.info("Validating chunks...")

        # Check metadata completeness
        required_metadata_keys = {"source_name", "doc_type"}
        incomplete_chunks = []

        for i, chunk in enumerate(chunks):
            if not all(key in chunk.metadata for key in required_metadata_keys):
                incomplete_chunks.append(i)

        # Calculate length statistics
        chunk_lengths = [len(chunk.page_content.split()) for chunk in chunks]

        report = {
            "total_chunks": len(chunks),
            "chunk_length_mean": sum(chunk_lengths) / len(chunk_lengths) if chunk_lengths else 0,
            "chunk_length_min": min(chunk_lengths) if chunk_lengths else 0,
            "chunk_length_max": max(chunk_lengths) if chunk_lengths else 0,
            "incomplete_metadata": len(incomplete_chunks),
            "empty_chunks": sum(1 for c in chunks if not c.page_content.strip()),
            "validation_passed": len(incomplete_chunks) == 0,
        }

        logger.info(f"  Total chunks: {report['total_chunks']}")
        logger.info(f"  Mean chunk length: {report['chunk_length_mean']:.0f} words")
        logger.info(f"  Min/Max length: {report['chunk_length_min']}/{report['chunk_length_max']} words")
        logger.info(f"  Incomplete metadata: {report['incomplete_metadata']}")
        logger.info(f"  Empty chunks: {report['empty_chunks']}")

        if report["validation_passed"]:
            logger.info("✓ All chunks passed validation")
        else:
            logger.warning(f"⚠ {report['incomplete_metadata']} chunks have incomplete metadata")

        return report


if __name__ == "__main__":
    # Quick sanity check
    pipeline = DocumentIngestionPipeline()

    logger.info("=== RedundancyAI Ingestion Pipeline Sanity Check ===")
    logger.info("")

    # Load documents
    documents = pipeline.load_documents()
    if not documents:
        logger.warning("No documents found. Have you downloaded them yet?")
        logger.info("Run: python scripts/download_sources.py")
    else:
        # Chunk documents
        chunks = pipeline.chunk_documents(documents)

        # Validate
        validation_report = pipeline.validate_chunks(chunks)

        # Print sample chunk
        if chunks:
            logger.info("")
            logger.info("Sample chunk (first 200 chars):")
            logger.info(f"  Content: {chunks[0].page_content[:200]}...")
            logger.info(f"  Metadata: {chunks[0].metadata}")
