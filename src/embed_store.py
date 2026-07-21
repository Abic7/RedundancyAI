"""Embedding and vector store management."""

from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from src.config import EMBEDDING_MODEL, CHROMA_PERSIST_DIR
from src.logger import setup_logger

logger = setup_logger(__name__)


class VectorStoreManager:
    """Manage embeddings and Chroma vector store."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize vector store manager.

        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.model_name = model_name
        self.embedding_model = None

    def _get_embedding_model(self):
        """Load embedding model (cached)."""
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = HuggingFaceEmbeddings(model_name=self.model_name)
            logger.info("✓ Embedding model loaded")
        return self.embedding_model

    def build_vectorstore(
        self, chunks: list[Document], persist_dir: str = CHROMA_PERSIST_DIR
    ):
        """
        Build Chroma vector store from chunks.

        Args:
            chunks: List of chunked documents with metadata
            persist_dir: Directory to persist Chroma DB

        Returns:
            Chroma vectorstore instance
        """
        persist_dir = Path(persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating Chroma vector store...")
        logger.info(f"  Chunks to embed: {len(chunks)}")
        logger.info(f"  Persist directory: {persist_dir}")

        embeddings = self._get_embedding_model()

        # Create Chroma vectorstore
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(persist_dir),
            collection_name="fair_work_docs",
        )

        logger.info(f"✓ Vector store created with {len(chunks)} chunks")
        return vectorstore

    def load_vectorstore(self, persist_dir: str = CHROMA_PERSIST_DIR):
        """
        Load persisted Chroma vector store.

        Args:
            persist_dir: Directory containing Chroma DB

        Returns:
            Chroma vectorstore instance
        """
        persist_dir = Path(persist_dir)

        if not persist_dir.exists():
            raise FileNotFoundError(f"Vector store not found at {persist_dir}")

        logger.info(f"Loading vector store from {persist_dir}...")

        embeddings = self._get_embedding_model()

        vectorstore = Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embeddings,
            collection_name="fair_work_docs",
        )

        logger.info("✓ Vector store loaded")
        return vectorstore
