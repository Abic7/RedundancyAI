# RedundancyAI — Open Source RAG Chatbot for Australian Redundancy Entitlements

**Status:** MVP Complete (8/10 Phases) | Production Ready  
**Last Updated:** 21 July 2026  
**License:** Apache 2.0

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

## System Architecture

```
Fair Work Documents (PDFs + Text)
        ↓
[Ingestion] - Load + chunk with metadata (949 chunks)
        ↓
[Embedding] - BAAI/bge-large-en-v1.5 (~1024-dim vectors)
        ↓
[Vector Store] - Chroma (persisted locally)
        ↓
[Retrieval] - Similarity search (top-8 chunks)
        ↓
[Confidence Gate] - Min similarity 0.25 (empirically tuned)
        ↓
[RAG Chain] - LangChain LCEL
  ├─ Inject source tags: [Source: DocumentName]
  ├─ Rerank: Cross-similarity (top-3)
  └─ LLM: LM Studio (Qwen-2.5 or Llama-2)
        ↓
[Output Validation]
  ├─ Extract citations from LLM response
  ├─ Verify citations in retrieved chunks
  ├─ Detect unsourced factual claims
  └─ Flag hallucinations
        ↓
[Injection Defense] - 9 attack patterns detected
  ├─ System overrides
  ├─ Rule overrides
  ├─ Persona swaps
  └─ Delimiter resets
        ↓
[Streamlit UI]
  ├─ Chat interface with message history
  ├─ Confidence indicators
  ├─ Source attribution
  └─ Safety warnings
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design decisions and data flows.

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
- 8GB RAM (recommended for 12B models)
- LM Studio running locally with a model loaded
  ```bash
  # Download and install LM Studio from https://lmstudio.ai
  # 
  # Recommended Models:
  #   • google/gemma-4-12b (12B) - Best quality ⭐
  #   • Qwen-2.5-7B-Instruct (7B) - Good balance
  #   • Llama-2-7B-Chat (7B) - Alternative
  #
  # Load model: LM Studio → Search → Download
  # Start server: LM Studio → Local Server → Start
  # Runs on http://localhost:1234
  ```

---

## Tech Stack (All Open Source)

| Component | Technology |
|-----------|------------|
| LLM | LM Studio + Gemma-4-12B (or Qwen-2.5, Llama-2) |
| Embeddings | sentence-transformers (BAAI/bge-large-en-v1.5) |
| Vector DB | Chroma (persisted locally) |
| RAG Framework | LangChain 0.3.0 + LCEL |
| UI | Streamlit 1.41 |
| Testing | pytest 8.0 + coverage |
| License | Apache 2.0 |

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

## Quality Gates (MVP Release)

| Gate | Target | Status |
|------|--------|--------|
| Citation Accuracy | 100% | ✅ Validated (Phase 8) |
| Hallucination Prevention | Detects unsourced claims | ✅ Implemented (Phase 5) |
| Retrieval Quality | 90%+ | ✅ Achieved 100% (Phase 4.5) |
| Confidence Threshold | 0.25 (empirical) | ✅ Tuned (Phase 6) |
| Injection Defense | Blocks 9 attack patterns | ✅ Tested (Phase 8) |
| Code Quality | ruff, mypy, black passing | ✅ CI/CD (Phase 8) |
| Test Coverage | 27+ unit tests | ✅ Added (Phase 8) |
| Reproducibility | <5 min setup | ✅ Automated (Phase 10) |

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

### LM Studio Setup Issues

**Q: "Failed to connect to LM Studio"**
```bash
# Verify server is running
curl http://localhost:1234/api/tags

# Restart LM Studio
# Open LM Studio → Local Server → Restart

# Check .env file has correct URL
cat .env | grep LLM_BASE_URL  # Should show http://localhost:1234/v1
```

**Q: "Model not found" error**
```bash
# Verify model is loaded in LM Studio
# LM Studio → Local Server → should show loaded model

# Download model if needed
# LM Studio → Search → "Qwen-2.5-7B-Instruct" → Download
```

**Q: Low confidence scores on valid questions**
- Confidence threshold is 0.25 (empirically tuned)
- If scoring 0.2-0.4: Consider the question borderline
- Check retrieval quality: `python scripts/tune_confidence_simple.py`
- Try larger model (13B+ instead of 7B) for better answers

### Vector Store Issues

**Q: "Vector store not found" error**
```bash
# Rebuild vector store
python scripts/build_index.py  # Takes 1-2 minutes

# Verify it was created
ls -la data/processed/chroma_db/
```

**Q: Low retrieval quality**
- Check document quality: `ls data/raw/`
- Verify chunk size: `echo $CHUNK_SIZE` (should be 700)
- Try re-ingesting: `rm -rf data/processed/chroma_db && python scripts/build_index.py`

### Test & Quality Assurance

**Q: "Tests failing in CI/CD"**
- Unit tests (27) should pass: `pytest tests/test_injection_detector.py tests/test_output_processor.py -v`
- E2E tests skip without LM Studio: `pytest tests/test_e2e.py -v` (marked @pytest.mark.skip)
- Check imports: All deprecated langchain imports replaced with langchain_core

**Q: Injection detected on legitimate question**
- Sensitivity is 0.5 (2+ patterns trigger block)
- Check `src/injection_detector.py` for patterns matched
- Adjust: `RAGChain(injection_sensitivity=0.7)` for stricter detection

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

---

## 📊 Architecture Diagrams

**New in v1.0:** Comprehensive architecture diagrams for system design, deployment, and security.

Five professional `.drawio` diagrams are included:
1. **System Architecture** — 5-layer pipeline with all components
2. **Data Flow** — Step-by-step execution with performance metrics
3. **Security Defense** — 6-layer protection stack
4. **Component Dependencies** — Module-level architecture
5. **Deployment Architecture** — v1.0 local setup + v2.0 roadmap

**Open them:**
- Online: https://app.diagrams.net/ → File → Open → select `.drawio` file
- Desktop: Download draw.io, double-click any `.drawio` file
- Guide: See `DIAGRAMS_GUIDE.md` for detailed instructions

**Export to:**
- PNG (embedded XML, stays editable in draw.io)
- SVG (vector, scales perfectly)
- PDF (print-friendly)

See `diagrams/README.md` for descriptions and use cases.

