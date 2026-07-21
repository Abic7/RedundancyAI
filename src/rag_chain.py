"""RAG Chain - LangChain LCEL implementation with citation enforcement."""

import logging
from typing import Optional
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config import (
    LLM_BASE_URL,
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    RETRIEVAL_K,
    RERANK_K,
    MIN_SIMILARITY_SCORE,
)
from src.prompts import RAG_PROMPT
from src.output_processor import OutputProcessor
from src.injection_detector import PromptInjectionDetector
from src.logger import setup_logger

logger = setup_logger(__name__)


class RAGChain:
    """RAG Chain with citation enforcement and injection defense."""

    def __init__(
        self,
        llm_base_url: str = LLM_BASE_URL,
        llm_model: str = LLM_MODEL_NAME,
        llm_temperature: float = LLM_TEMPERATURE,
        embedding_model: str = EMBEDDING_MODEL,
        chroma_dir: str = CHROMA_PERSIST_DIR,
        retrieval_k: int = RETRIEVAL_K,
        rerank_k: int = RERANK_K,
        min_similarity: float = MIN_SIMILARITY_SCORE,
        injection_sensitivity: float = 0.7,
    ):
        """
        Initialize RAG chain.

        Args:
            llm_base_url: LM Studio API URL
            llm_model: Model name to use
            llm_temperature: LLM temperature (0.0-1.0)
            embedding_model: Embedding model name
            chroma_dir: Chroma vector store directory
            retrieval_k: Number of chunks to retrieve
            rerank_k: Number of chunks to keep after reranking
            min_similarity: Minimum similarity score to proceed (confidence gate)
            injection_sensitivity: Injection detection sensitivity (0.0-1.0)
        """
        self.llm_base_url = llm_base_url
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        self.embedding_model = embedding_model
        self.chroma_dir = chroma_dir
        self.retrieval_k = retrieval_k
        self.rerank_k = rerank_k
        self.min_similarity = min_similarity

        # Initialize components
        self._vectorstore = None
        self._llm = None
        self._injection_detector = PromptInjectionDetector(sensitivity=injection_sensitivity)
        self._output_processor = OutputProcessor()

    @property
    def vectorstore(self) -> Chroma:
        """Lazy-load vector store."""
        if self._vectorstore is None:
            logger.info(f"Loading vector store from {self.chroma_dir}...")
            embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
            self._vectorstore = Chroma(
                persist_directory=self.chroma_dir,
                embedding_function=embeddings,
                collection_name="fair_work_docs",
            )
            logger.info("✓ Vector store loaded")
        return self._vectorstore

    @property
    def llm(self) -> ChatOllama:
        """Lazy-load LLM."""
        if self._llm is None:
            logger.info(f"Connecting to LM Studio at {self.llm_base_url}...")
            self._llm = ChatOllama(
                base_url=self.llm_base_url,
                model=self.llm_model,
                temperature=self.llm_temperature,
            )
            logger.info(f"✓ Connected to {self.llm_model}")
        return self._llm

    def _retrieve_chunks(self, question: str) -> list:
        """
        Retrieve top-k chunks from vector store.

        Returns:
            List of Document objects with metadata
        """
        logger.debug(f"Retrieving {self.retrieval_k} chunks for question: {question}")
        chunks = self.vectorstore.similarity_search_with_scores(question, k=self.retrieval_k)

        # Extract chunks and scores
        results = []
        for chunk, score in chunks:
            results.append(
                {
                    "content": chunk.page_content,
                    "source": chunk.metadata.get("source_name", "Unknown"),
                    "similarity": score,
                    "metadata": chunk.metadata,
                }
            )

        logger.debug(f"Retrieved {len(results)} chunks with avg similarity: {sum(r['similarity'] for r in results) / len(results):.3f}")
        return results

    def _format_context(self, chunks: list) -> str:
        """
        Format retrieved chunks into context string with inline source tags.

        Format:
            [Source: SourceName]
            Chunk text...

            [Source: SourceName]
            Chunk text...
        """
        if not chunks:
            return "No relevant information found in the knowledge base."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["source"]
            content = chunk["content"]
            context_parts.append(f"[Source: {source}]\n{content}")

        return "\n\n".join(context_parts)

    def _confidence_gate(self, chunks: list) -> tuple[bool, float]:
        """
        Apply confidence gate based on retrieval similarity.

        Returns:
            (should_proceed, max_similarity)
        """
        if not chunks:
            return False, 0.0

        max_similarity = max(chunk["similarity"] for chunk in chunks)
        should_proceed = max_similarity >= self.min_similarity

        logger.debug(f"Confidence gate: max_similarity={max_similarity:.3f}, threshold={self.min_similarity}, proceed={should_proceed}")

        return should_proceed, max_similarity

    def _rerank_chunks(self, chunks: list) -> list:
        """
        Rerank chunks using simple heuristic (keep top-k by similarity).

        In production, this could use a cross-encoder model.
        """
        sorted_chunks = sorted(chunks, key=lambda x: x["similarity"], reverse=True)
        reranked = sorted_chunks[: self.rerank_k]

        logger.debug(f"Reranked {len(chunks)} chunks to top {len(reranked)}")
        return reranked

    def answer_question(self, question: str) -> dict:
        """
        Answer a question using RAG chain.

        Returns:
            {
                "question": str,
                "answer": str,
                "sources": [{"name": str, "chunk": str}],
                "confidence": float,
                "hallucination_detected": bool,
                "injection_detected": bool,
                "metadata": {
                    "retrieval_time": float,
                    "llm_time": float,
                    "processing_time": float,
                }
            }
        """
        import time
        start_time = time.time()

        logger.info(f"Processing question: {question}")

        # Step 1: Injection detection
        injection_result = self._injection_detector.detect(question)
        logger.info(f"Injection detection: {injection_result['threat_level'].value} (confidence: {injection_result['confidence']:.2f})")

        if injection_result["is_blocked"]:
            logger.warning(f"Injection blocked: {injection_result['reason']}")
            return {
                "question": question,
                "answer": "I don't have reliable information about that. Please consult Fair Work Australia directly at https://www.fairwork.gov.au or call 13 13 94.",
                "sources": [],
                "confidence": 0.0,
                "hallucination_detected": False,
                "injection_detected": True,
                "injection_threat": injection_result,
                "metadata": {},
            }

        # Step 2: Retrieval
        retrieval_start = time.time()
        chunks = self._retrieve_chunks(question)
        retrieval_time = time.time() - retrieval_start
        logger.info(f"Retrieved {len(chunks)} chunks in {retrieval_time:.2f}s")

        # Step 3: Confidence gate
        should_proceed, max_similarity = self._confidence_gate(chunks)
        if not should_proceed:
            logger.info(f"Confidence gate failed: max_similarity={max_similarity:.3f} < threshold={self.min_similarity}")
            return {
                "question": question,
                "answer": "I don't have reliable information about that. Please consult Fair Work Australia directly at https://www.fairwork.gov.au or call 13 13 94.",
                "sources": [{"name": chunk["source"], "chunk": chunk["content"][:200]} for chunk in chunks],
                "confidence": max_similarity,
                "hallucination_detected": False,
                "injection_detected": False,
                "metadata": {"retrieval_time": retrieval_time},
            }

        # Step 4: Reranking
        chunks = self._rerank_chunks(chunks)
        logger.info(f"Reranked to top {len(chunks)} chunks")

        # Step 5: Format context
        context = self._format_context(chunks)

        # Step 6: LLM call
        llm_start = time.time()
        logger.info("Calling LLM...")

        try:
            # Format prompt and call LLM
            prompt = RAG_PROMPT.format(context=context, question=question)
            response = self.llm.invoke(prompt)
            llm_output = response.content if hasattr(response, "content") else str(response)
            llm_time = time.time() - llm_start
            logger.info(f"LLM response received in {llm_time:.2f}s")

        except Exception as e:
            logger.error(f"LLM call failed: {e}", exc_info=True)
            return {
                "question": question,
                "answer": "An error occurred while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "hallucination_detected": False,
                "injection_detected": False,
                "metadata": {"retrieval_time": retrieval_time, "error": str(e)},
            }

        # Step 7: Output processing (citation extraction & validation)
        processed = self._output_processor.process_output(
            llm_output,
            retrieved_chunks=chunks,
            question=question,
        )

        # Step 8: Confidence score
        confidence = self._calculate_confidence(chunks, processed)

        # Compile response
        total_time = time.time() - start_time

        response = {
            "question": question,
            "answer": processed["answer"],
            "sources": processed["sources"],
            "confidence": confidence,
            "hallucination_detected": processed["hallucination_detected"],
            "injection_detected": False,
            "metadata": {
                "retrieval_time": retrieval_time,
                "llm_time": llm_time,
                "processing_time": total_time,
                "chunks_retrieved": len(chunks),
                "max_similarity": max_similarity,
            },
        }

        logger.info(f"Question processed in {total_time:.2f}s with confidence {confidence:.2f}")
        return response

    def _calculate_confidence(self, chunks: list, processed_output: dict) -> float:
        """
        Calculate confidence score based on:
        - Max retrieval similarity
        - Citation correctness
        - Hallucination detection
        """
        if not chunks:
            return 0.0

        max_similarity = max(chunk["similarity"] for chunk in chunks)

        # Reduce confidence if hallucination detected
        if processed_output["hallucination_detected"]:
            max_similarity *= 0.3

        # Reduce confidence if citations are questionable
        if processed_output.get("unverified_citations", 0) > 0:
            max_similarity *= 0.7

        return min(1.0, max_similarity)


# Factory function for testing
def create_rag_chain(**kwargs) -> RAGChain:
    """Create and return a RAG chain instance."""
    return RAGChain(**kwargs)
