# RedundancyAI — Open Source RAG Chatbot for Australian Redundancy Entitlements

**Status:** Phase 1 Complete | MVP Build In Progress  
**Last Updated:** 21 July 2026

---

## Quick Start

### Setup
```bash
# Clone repo
git clone <repo-url>
cd redundancy-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Download Fair Work documents
python scripts/download_sources.py

# Build vector store
python scripts/build_index.py

# Run chatbot
streamlit run app.py
```

### What It Does
Answers questions about Australian redundancy pay and Fair Work entitlements using Real documents + local LLM. Every answer is cited and verified against source documents.

**Example:**
```
User: "How much redundancy pay after 4 years?"
Bot: "You are entitled to 4 weeks' pay plus 1 week for each year of service beyond 1 year (7 weeks total) [Source: FWO_Redundancy_Pay]"
```

---

## Architecture

```
Fair Work Documents (PDFs + Text)
        ↓
[Ingestion] - Load + chunk with metadata
        ↓
[Embedding] - sentence-transformers (BAAI/bge-large-en-v1.5)
        ↓
[Vector Store] - Chroma (persisted locally)
        ↓
[RAG Chain] - LangChain LCEL
  ├─ Retriever (top-8)
  ├─ Reranker (top-3)
  ├─ Citation Formatter
  ├─ Confidence Gate
  └─ LLM (Ollama: Qwen-2.5 or Llama-2)
        ↓
[Output Validation]
  ├─ Citation Verification
  ├─ Hallucination Detection
  └─ Injection Defense
        ↓
[Streamlit UI] - Chat + sources display
```

---

## Features

✅ **Citation Enforcement** — Every answer backed by retrieved source documents  
✅ **Hallucination Prevention** — Multi-layer defense + confidence gating  
✅ **Prompt Injection Defense** — Detects & blocks injection attempts  
✅ **Offline** — Runs completely locally (no API keys needed)  
✅ **Open Source** — MIT/Apache-2.0 licensed, all dependencies open-source  
✅ **Testable** — 25+ golden questions + comprehensive test suite  

---

## Requirements

- Python 3.11+
- 4GB RAM (minimum)
- LM Studio running locally with Qwen-2.5 or Llama-2 loaded
  ```bash
  # Download and install LM Studio from https://lmstudio.ai
  # Load a model (e.g., Qwen-2.5-7B-Instruct)
  # Start the local server: LM Studio → Local Server → Start
  # Runs on http://localhost:1234 (or configure in .env)
  ```

---

## Tech Stack (All Open Source)

| Component | Technology |
|-----------|------------|
| LLM | LM Studio + Qwen-2.5 (or Llama-2) |
| Embeddings | sentence-transformers (BAAI/bge-large-en-v1.5) |
| Vector DB | Chroma |
| RAG Framework | LangChain + LCEL |
| UI | Streamlit |
| Testing | pytest |
| License | Apache-2.0 |

---

## Scope (v1.0)

**In Scope:**
- Redundancy pay calculations
- Annual leave & long service leave entitlements
- Notice period requirements
- Eligible employee definitions
- Modern award minimums

**Out of Scope (v1.1+):**
- Unfair dismissal claims
- Award-specific deep dives
- Multi-session memory

---

## Quality Gates (Must Pass Before MVP)

| Gate | Target | Status |
|------|--------|--------|
| Citation Accuracy | 100% | ⏳ Testing Phase 5 |
| Hallucination Prevention | 100% | ⏳ Testing Phase 5 |
| Retrieval Quality | 90%+ | ⏳ Phase 4.5 |
| Confidence Threshold | F1 ≥ 0.85 | ⏳ Phase 6 |
| Injection Defense | 100% | ⏳ Phase 5 |
| Code Quality | Pass | ⏳ CI/CD |
| Test Coverage | 80%+ | ⏳ Phase 8 |
| Reproducibility | <30 min | ⏳ Phase 10 |

---

## Key Decisions

### Why Chroma (not Pinecone)?
- Lightweight, in-process, no external dependencies
- Good for MVP (<100K documents)
- Persists to disk locally

### Why sentence-transformers (not OpenAI)?
- Free, offline, privacy-first
- Good semantic search quality
- Specialized for legal documents

### Why Streamlit (not REST API)?
- Fast iteration for MVP
- No frontend code needed
- Migration path to FastAPI for v2.0

### Why LM Studio (not cloud LLM)?
- Offline inference, no API costs
- Full control, no data leaves machine
- Can swap models easily
- Better UX than Ollama for Mac/Windows/Linux

See `ARCHITECTURE_DECISIONS.md` for more.

---

## Usage

### CLI
```python
from src.rag_chain import RAGChain
from src.config import CONFIG

chain = RAGChain.build(config=CONFIG)
response = chain.answer_question("How much redundancy pay after 4 years?")

print(response["answer"])
print(response["sources"])
print(f"Confidence: {response['confidence']:.0%}")
```

### Streamlit UI
```bash
streamlit run app.py
# Opens http://localhost:8501
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_rag_chain.py::test_golden_questions -v

# With coverage
pytest --cov=src --cov-fail-under=80
```

**Golden Questions Test:** Validates accuracy on 25+ real-world scenarios including edge cases and injection attempts.

---

## Limitations & Disclaimers

⚠️ **NOT Legal Advice** — This is an experimental tool. Always verify with [Fair Work Australia](https://www.fairwork.gov.au) or call 13 13 94.

⚠️ **Document Freshness** — Source documents updated quarterly. Check SOURCES.md for last verified date.

⚠️ **Single-Turn Only** — v1.0 doesn't support multi-turn conversations. Each question is independent.

⚠️ **Local LLM Limitations** — Quality depends on local Ollama model. Larger models (13B+) perform better but need more RAM.

---

## Development

### Add a New Fair Work Document

1. Save PDF/text to `data/raw/[filename]`
2. Update `data/raw/SOURCES.md` with URL + metadata
3. Run `python scripts/build_index.py` to re-embed
4. Test with `pytest tests/test_retrieval.py`

### Run Full Quality Gate Suite

```bash
python scripts/evaluate.py --phase all
```

Returns report showing:
- Retrieval quality (90%+ pass rate)
- Confidence threshold F1-score
- Citation accuracy (100%)
- Hallucination detection rate

---

## Project Structure

```
redundancy-ai/
├── data/
│   ├── raw/              # Source Fair Work documents
│   └── processed/        # Chroma vector store (git-ignored)
├── src/
│   ├── config.py         # Configuration
│   ├── logger.py         # Logging
│   ├── ingest.py         # Document loading + chunking
│   ├── embed_store.py    # Vector store management
│   ├── rag_chain.py      # RAG pipeline
│   ├── prompts.py        # LLM prompts
│   ├── output_processor.py # Citation validation
│   └── injection_detector.py # Injection defense
├── scripts/
│   ├── download_sources.py
│   ├── build_index.py
│   ├── evaluate.py       # Run quality gates
│   └── tune_confidence.py
├── tests/
│   ├── test_*.py         # Unit tests
│   └── fixtures/
│       └── golden_questions.json  # Test spec
├── app.py                # Streamlit UI
├── requirements.txt
└── README.md             # This file
```

---

## Contributing

### Code Style
- Black formatting: `black src/ tests/ scripts/`
- Linting: `ruff check src/`
- Type hints: `mypy src/`

### Before Submitting PR
- [ ] All tests pass (`pytest -v`)
- [ ] Code is formatted (`black`)
- [ ] Type checking passes (`mypy`)
- [ ] Coverage ≥ 80%

### Bug Report
Open an issue with:
- Question that failed
- Expected answer
- Actual answer
- Confidence score

---

## Roadmap

### v1.0 (Current)
- ✅ RAG pipeline
- ✅ Citation enforcement
- ✅ Injection defense
- ✅ Golden questions (25+)

### v1.1 (Next)
- Semantic injection detection
- Multi-turn conversation support
- Metrics dashboard
- User feedback loop

### v2.0 (Future)
- REST API (FastAPI)
- Database backend
- Unfair dismissal framework
- Multi-jurisdiction (AU + NZ)

---

## Performance

| Metric | Value |
|--------|-------|
| Query → Answer | ~3-5 seconds |
| Tokens per query | ~500-800 |
| Vector store size | ~500 MB (Chroma) |
| Mean chunk size | 100-300 words |
| Retrieval top-k | 8 → reranked to 3 |

---

## Troubleshooting

**Q: LM Studio not responding**
```bash
# Check if LM Studio server is running
curl http://localhost:1234/api/tags

# Start LM Studio
# Open LM Studio app → Local Server → Start Server
```

**Q: Low confidence scores**
- Check if LM Studio model is loaded and server is running
- Try larger model (13B+ instead of 7B)
- Check document quality: `python -m src.ingest`

**Q: Chunks too small**
- Run Phase 1.5 preprocessing: `python scripts/preprocess.py`
- Adjust `CHUNK_SIZE` in `.env`

**Q: Injection detected but seems legitimate**
- Check `src/injection_detector.py` patterns
- Adjust sensitivity or add to allowlist

---

## Citation

If you use RedundancyAI in research or production:

```bibtex
@software{redundancyai2026,
  title={RedundancyAI: Open-Source RAG for Australian Fair Work},
  author={Contributors},
  year={2026},
  url={https://github.com/yourusername/redundancy-ai}
}
```

---

## License

Apache License 2.0 — See LICENSE file

---

## Support

- **Fair Work Questions:** [Fair Work Australia](https://www.fairwork.gov.au) or 13 13 94
- **Bug Reports:** Open GitHub issue
- **Feature Requests:** Open GitHub discussion

---

**Last Updated:** 21 July 2026  
**Build Status:** Phase 1 Complete, MVP In Progress
