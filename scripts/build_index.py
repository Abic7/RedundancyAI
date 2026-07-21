"""Build Chroma vector store from ingested documents."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingest import DocumentIngestionPipeline
from src.embed_store import VectorStoreManager
from src.config import RAW_DATA_DIR, CHROMA_PERSIST_DIR
from src.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Build vector store from Fair Work documents."""

    logger.info("=== RedundancyAI Vector Store Builder ===")
    logger.info("")

    try:
        # Step 1: Load and chunk documents
        logger.info("Step 1: Loading documents from data/raw/")
        pipeline = DocumentIngestionPipeline()
        documents = pipeline.load_documents(RAW_DATA_DIR)

        if not documents:
            logger.error("No documents found in data/raw/")
            return 1

        logger.info(f"Loaded {len(documents)} documents")

        # Step 2: Chunk documents
        logger.info("")
        logger.info("Step 2: Chunking documents")
        chunks = pipeline.chunk_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")

        # Step 3: Validate chunks
        logger.info("")
        logger.info("Step 3: Validating chunks")
        validation = pipeline.validate_chunks(chunks)

        if not validation["validation_passed"]:
            logger.error("Chunk validation failed")
            return 1

        logger.info("✓ All chunks validated")

        # Step 4: Build embeddings and vector store
        logger.info("")
        logger.info("Step 4: Building embeddings (this may take a few minutes)...")
        manager = VectorStoreManager()
        vectorstore = manager.build_vectorstore(chunks, CHROMA_PERSIST_DIR)
        logger.info(f"✓ Vector store built and persisted to {CHROMA_PERSIST_DIR}")

        # Step 5: Verify retrieval works
        logger.info("")
        logger.info("Step 5: Verifying retrieval")
        test_query = "redundancy pay"
        results = vectorstore.similarity_search(test_query, k=3)

        if not results:
            logger.error("Retrieval test failed - no results returned")
            return 1

        logger.info(f"✓ Retrieval works - found {len(results)} results for '{test_query}'")
        logger.info(f"  Top result: {results[0].page_content[:100]}...")
        logger.info(f"  Source: {results[0].metadata.get('source_name', 'Unknown')}")

        logger.info("")
        logger.info("=== BUILD COMPLETE ===")
        logger.info("")
        logger.info(f"Vector store ready at: {CHROMA_PERSIST_DIR}")
        logger.info(f"Total chunks indexed: {len(chunks)}")
        logger.info("Next: Phase 4.5 - Retrieval Quality Audit")

        return 0

    except Exception as e:
        logger.error(f"Build failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
