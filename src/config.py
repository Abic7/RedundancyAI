"""Configuration management for RedundancyAI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TESTS_DIR = PROJECT_ROOT / "tests"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# LLM Configuration
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen2.5:7b-instruct")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")

# Vector Store Configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(PROCESSED_DATA_DIR / "chroma_db"))

# Chunking & Retrieval Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "8"))
RERANK_K = int(os.getenv("RERANK_K", "3"))

# Confidence Gating Configuration (tuned via Phase 6 calibration)
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
MIN_SIMILARITY_SCORE = float(os.getenv("MIN_SIMILARITY_SCORE", "0.25"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Source Documents Registry
SOURCES_REGISTRY_FILE = RAW_DATA_DIR / "SOURCES.md"
