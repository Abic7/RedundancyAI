# RedundancyAI Dependencies & Library Versions

**Last Updated:** 21 July 2026  
**Python:** 3.11+

## Core Dependencies

### LLM & RAG Framework

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| `langchain` | 0.3.0 | ✅ Current | Main framework |
| `langchain-core` | 0.3.0 | ✅ Current | Core LCEL |
| `langchain-community` | 0.3.0 | ✅ Current | Standard integrations |
| `langchain-ollama` | 0.1.2 | ✅ Current | LM Studio integration |
| `langchain-chroma` | 0.1.0 | ✅ Current | Vector store (replaces `langchain_community.vectorstores.Chroma`) |
| `langchain-huggingface` | 0.0.1 | ✅ Current | Embeddings (replaces `langchain_community.embeddings.HuggingFaceEmbeddings`) |

### Vector Database & Embeddings

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| `chromadb` | 0.5.3 | ✅ Current | Vector store backend |
| `sentence-transformers` | 3.0.1 | ✅ Current | Embedding model (BAAI/bge-large-en-v1.5) |

### Document Processing

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| `pypdf` | 5.1.0 | ✅ Current | PDF parsing |
| `beautifulsoup4` | 4.12.3 | ✅ Current | HTML parsing |
| `lxml` | 5.2.2 | ✅ Current | XML/HTML support |

### Web & UI

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| `streamlit` | 1.41.0 | ✅ Current | Web chatbot interface |
| `requests` | 2.32.3 | ✅ Current | HTTP client |

### Utilities

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| `python-dotenv` | 1.0.1 | ✅ Current | Environment variables |
| `pydantic` | 2.9.0 | ✅ Current | Data validation |

### Development & Testing

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| `pytest` | 8.0.0 | ✅ Current | Testing framework |
| `pytest-cov` | 5.0.0 | ✅ Current | Coverage reports |
| `black` | 24.1.1 | ✅ Current | Code formatting |
| `ruff` | 0.3.3 | ✅ Current | Linting |
| `mypy` | 1.10.0 | ✅ Current | Type checking |

## Deprecated Libraries (Removed)

### LangChain Community (Replaced)

| Old Import | New Import | Reason |
|-----------|-----------|--------|
| `from langchain.schema import Document` | `from langchain_core.documents import Document` | Moved to core |
| `from langchain.prompts import PromptTemplate` | `from langchain_core.prompts import PromptTemplate` | Moved to core |
| `from langchain_community.vectorstores import Chroma` | `from langchain_chroma import Chroma` | Dedicated package |
| `from langchain_community.embeddings import HuggingFaceEmbeddings` | `from langchain_huggingface import HuggingFaceEmbeddings` | Dedicated package |

## Migration Checklist

### Done ✅

- [x] Updated `requirements.txt` to latest stable versions
- [x] Replaced `langchain_community.vectorstores.Chroma` → `langchain_chroma.Chroma`
- [x] Replaced `langchain_community.embeddings.HuggingFaceEmbeddings` → `langchain_huggingface.HuggingFaceEmbeddings`
- [x] Replaced `langchain.schema.Document` → `langchain_core.documents.Document`
- [x] Replaced `langchain.prompts.PromptTemplate` → `langchain_core.prompts.PromptTemplate`
- [x] Updated all imports in `src/*.py`
- [x] Updated all imports in `tests/*.py`
- [x] Tested compatibility with Python 3.11

### Installation

```bash
# Fresh install
pip install -r requirements.txt

# Upgrade existing
pip install -U -r requirements.txt

# Verify installation
python -c "import langchain; print(langchain.__version__)"
python -c "import chromadb; print(chromadb.__version__)"
python -c "from sentence_transformers import SentenceTransformer; print('OK')"
```

## Known Issues & Workarounds

### Deprecation Warnings

LangChain 0.3.0 still emits warnings about the old APIs, but the new imports work correctly:

```
LangChainDeprecationWarning: The class `HuggingFaceEmbeddings` was deprecated...
```

These are harmless and will be removed in LangChain 1.0.

### Chroma Persistence

Vector store persists to `data/processed/chroma_db/` automatically. No migration needed if upgrading chromadb versions.

## Testing Compatibility

All tests pass with:
- Python 3.11.15
- pytest 8.0.0
- pytest-cov 5.0.0

Run tests with coverage:

```bash
pytest tests/ -v --cov=src --cov-fail-under=80
```

## Performance Notes

- **Embedding Model:** BAAI/bge-large-en-v1.5 (~4GB)
  - Downloads automatically on first use
  - Cached in `~/.cache/huggingface/`
  - Can take 1-2 minutes to load first time

- **Chroma Retrieval:** ~100ms per query (in-process)

- **LM Studio Latency:** 1-3 seconds per response (depends on model size)

## Future Upgrades

### v1.1 Roadmap

- [ ] Support for `langchain==1.0` (stable API)
- [ ] Migration to `langchain-chroma` for better persistence
- [ ] Consider `langchain-ollama` enhancements

### Monitoring

Check for new versions:

```bash
pip list --outdated
```

## Support

For library compatibility issues, check:
- LangChain Docs: https://python.langchain.com/
- Chroma Docs: https://docs.trychroma.com/
- Hugging Face Hub: https://huggingface.co/
