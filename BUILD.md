# RedundancyAI Build Guide

**Status:** Phases 1A-1B Complete | Phase 2 Ready to Start  
**Last Updated:** 21 July 2026

---

## Current Status

| Phase | Task | Status | Time |
|-------|------|--------|------|
| 1A | Repository + dependencies | ✅ DONE | 2h |
| 1B | Document acquisition | ✅ DONE | 2h |
| 2 | Embedding & vector store | ⏳ NEXT | 2h |
| 4.5 | Retrieval quality audit | ⏳ NEXT | 2h |
| 5 | RAG chain + injection defense | ⏳ Phase 2 | 6h |
| 6 | Confidence threshold tuning | ⏳ Phase 2 | 2h |
| 7 | Streamlit UI | ⏳ Phase 2 | 2h |
| 8 | Testing & metrics | ⏳ Phase 2 | 4h |
| 9 | Documentation | ⏳ Phase 3 | 2h |
| 10 | CI/CD & launch | ⏳ Phase 3 | 2h |

**Total Remaining:** ~25 hours (1.5 weekends)

---

## What's Done

### ✅ Phase 1A: Setup (2 hours)
- Python venv created
- All dependencies installed
- Directory structure created
- Configuration files ready
- GitHub Actions CI/CD configured
- Test infrastructure created (fixtures, test cases)

### ✅ Phase 1B: Documents (2 hours)
- 5 Fair Work documents acquired (real + mock)
- Ingestion pipeline tested
- **949 chunks created** (chunk_size=700, overlap=100)
- All metadata intact (source_name, doc_type, url, retrieved_at)
- Validation passed

### Files Ready to Use
```
src/
  ├── config.py          ✓
  ├── logger.py          ✓
  ├── ingest.py          ✓ (tested)
  ├── prompts.py         ✓
  ├── output_processor.py ✓ (tested)
  └── injection_detector.py (to implement Phase 5)

tests/
  ├── test_output_processor.py ✓ (ready)
  └── fixtures/golden_questions.json ✓ (14 + 4 injection tests)

data/
  ├── raw/               ✓ (5 documents)
  ├── processed/         (will contain Chroma DB after Phase 2)
  └── raw/SOURCES.md     ✓ (document registry)
```

---

## Next: Phase 2 (Day 2 AM, 2 hours)

### Goal
Build Chroma vector store from 949 chunks

### Checklist
- [ ] Activate venv: `venv\Scripts\Activate.ps1`
- [ ] Run: `python scripts/build_index.py`
- [ ] Verify: `data/processed/chroma_db/` created
- [ ] Test: `python -c "from src.embed_store import load_vectorstore; vs = load_vectorstore(); print(vs.similarity_search('redundancy pay', k=3))"`
- [ ] Expected: 3 relevant chunks returned with similarity scores
- [ ] Expected: Metadata intact on returned chunks

### If Fails
**Issue:** Embedding model not downloaded
```bash
# Install manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-large-en-v1.5')"
```

**Issue:** Out of memory
- Use smaller model: `BAAI/bge-small-en-v1.5`
- Or close other applications

---

## Then: Phase 4.5 (Day 2 AM, 2 hours)

### Goal
Verify retrieval quality before building RAG chain

### Checklist
- [ ] Run retrieval tests on 10 sample questions
- [ ] Top-3 results must be relevant for 90%+ of queries
- [ ] Metadata (source_name) must be intact
- [ ] If < 90% pass: investigate embedding model or chunk size

### Test Queries
```
1. How much redundancy pay after 4 years?
2. What's the notice period?
3. Annual leave entitlements?
4. Who's eligible?
5. Long service leave?
6. Part-time calculation?
7. Unpaid entitlements?
8. Award minimums?
9. Modern award rates?
10. (Off-topic for refusal test) What's the capital of France?
```

### Success Criteria
- Questions 1-8: Relevant chunks in top-3
- Question 9-10: Low similarity scores (<0.3)
- Metadata complete on all results

---

## Then: Phase 5 (Day 2 AM-PM, 6 hours)

### Goal
Build RAG chain with citation enforcement + injection defense

### Checklist
- [ ] Implement RAG chain (LCEL)
- [ ] Add injection detector (`src/injection_detector.py`)
- [ ] Update system prompt with anti-injection rules
- [ ] Implement output validation (citation verification)
- [ ] Test golden questions (should answer core FAQ, refuse off-topic)
- [ ] Test injection attempts (should refuse/warn all 4 types)

### Key Implementation Points
```python
# Phase 5 will use existing modules:
from src.ingest import DocumentIngestionPipeline
from src.embed_store import VectorStoreManager
from src.rag_chain import RAGChainBuilder  # To implement
from src.prompts import SYSTEM_PROMPT
from src.output_processor import OutputProcessor  # Existing
from src.injection_detector import PromptInjectionDetector  # To implement
```

### Test
```bash
pytest tests/test_rag_chain.py -v
pytest tests/test_prompt_injection.py -v  # New file
```

---

## Then: Phase 6 (Day 2 PM, 2 hours)

### Goal
Find optimal confidence threshold empirically

### Checklist
- [ ] Run 15 test questions at 5 thresholds (0.2, 0.3, 0.4, 0.5, 0.6)
- [ ] Measure precision, recall, F1 at each threshold
- [ ] Choose threshold with F1 ≥ 0.85
- [ ] Update `CONFIDENCE_THRESHOLD` in `src/config.py`
- [ ] Document results in metrics output

### Expected Output
```
Threshold 0.2: Precision=0.60, Recall=0.95, F1=0.74
Threshold 0.3: Precision=0.75, Recall=0.90, F1=0.82
Threshold 0.4: Precision=0.88, Recall=0.85, F1=0.86 ← OPTIMAL
Threshold 0.5: Precision=0.95, Recall=0.75, F1=0.84
Threshold 0.6: Precision=0.98, Recall=0.60, F1=0.74
```

---

## Then: Phase 7 (Day 2 PM, 2 hours)

### Goal
Build Streamlit UI

### Checklist
- [ ] Create `app.py` with chat interface
- [ ] Display sources below each answer
- [ ] Show confidence indicator
- [ ] Display disclaimer banner
- [ ] Test: `streamlit run app.py`
- [ ] Manual test: Ask 3 questions, verify sources show, check confidence

### Key Components
```python
# app.py will use:
from src.rag_chain import RAGChain
import streamlit as st

chain = RAGChain.build(config=CONFIG)

# Chat loop
for message in st.chat_input(...):
    response = chain.answer_question(message)
    st.write(response["answer"])
    st.write(response["sources"])
    st.write(f"Confidence: {response['confidence']:.0%}")
```

---

## Then: Phase 8 (Day 2 PM - Day 3 AM, 4 hours)

### Goal
Comprehensive testing + quality gates

### Checklist
- [ ] Run golden questions test: `pytest tests/test_rag_chain.py::test_golden_questions -v`
- [ ] All 25+ questions must pass (should_answer vs should_refuse)
- [ ] Run injection defense test: `pytest tests/test_prompt_injection.py -v`
- [ ] All 4 injection types must be refused or low-confidence
- [ ] Run full suite: `pytest --cov=src --cov-fail-under=80`
- [ ] Coverage must be ≥ 80%

### Test Results Required
```
test_golden_questions_accuracy: 25/25 PASSED ✓
test_injection_defense: 4/4 PASSED ✓
test_hallucination_prevention: PASSED ✓
test_citation_accuracy: PASSED ✓
Coverage: 82% ✓
```

### If Tests Fail
- **Golden questions:** Check retrieval quality (Phase 4.5)
- **Injection defense:** Check system prompt + detector patterns
- **Citation accuracy:** Check output processor validation
- **Coverage:** Add tests for uncovered code paths

---

## Then: Phase 9 (Day 3 AM, 2 hours)

### Goal
Documentation complete + ready to ship

### Checklist
- [ ] README.md complete (setup, architecture, usage)
- [ ] ARCHITECTURE_DECISIONS.md created (why we chose each tool)
- [ ] This BUILD.md updated with final status
- [ ] CONTRIBUTING.md created (how to add docs, report bugs)
- [ ] CHANGELOG.md created (v1.0 changes)

### Files to Create
```
README.md ✓ (already done)
ARCHITECTURE_DECISIONS.md (Chroma why, StreamLit why, etc.)
CONTRIBUTING.md (PR process, code style)
CHANGELOG.md (v1.0 release notes)
```

---

## Finally: Phase 10 (Day 3, 2 hours)

### Goal
CI/CD verification + reproducibility test

### Checklist
- [ ] GitHub Actions workflows pass: `pytest`, `lint`
- [ ] Fresh install test on clean machine/venv
  - [ ] Clone repo
  - [ ] `pip install -r requirements.txt`
  - [ ] `python scripts/download_sources.py`
  - [ ] `python scripts/build_index.py`
  - [ ] `pytest tests/ -v` (all pass)
  - [ ] `streamlit run app.py` (starts without errors)
  - [ ] Time to complete: < 30 minutes
- [ ] All 8 quality gates passing

### Quality Gates (Final Check)
```
Gate 1: Citation Accuracy       ✓ (100%)
Gate 2: Hallucination Prevention ✓ (100%)
Gate 3: Retrieval Quality       ✓ (90%+)
Gate 4: Confidence Threshold    ✓ (F1 ≥ 0.85)
Gate 5: Injection Defense       ✓ (100%)
Gate 6: Code Quality            ✓ (lint pass)
Gate 7: Test Coverage           ✓ (80%+)
Gate 8: Reproducibility         ✓ (<30 min)
```

### Launch Deliverables
- ✅ GitHub repo (public, Apache-2.0)
- ✅ README.md + ARCHITECTURE_DECISIONS.md
- ✅ All tests passing (pytest)
- ✅ CI/CD working (GitHub Actions)
- ✅ Reproducible from scratch

---

## Important Notes

### Document Quality Issue (Phase 1.5 Improvement)
**Issue Found:** Chunks averaging 29 words (too small)
**Impact:** Poor retrieval quality
**Solution:** Phase 1.5 - Document preprocessing
- Strip HTML boilerplate
- Merge short paragraphs
- Target: 100-300 words per chunk
**Timing:** Insert between Phase 1B and Phase 2 if needed

### Scope Lock
**Do NOT add in v1.0:**
- Unfair dismissal framework
- Multi-turn conversations
- Multi-session memory
- REST API
- Admin panel

These are v1.1+ features. Document but don't implement.

---

## Commands Quick Reference

```bash
# Activate
venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate   # Linux/Mac

# Build
python scripts/download_sources.py
python scripts/build_index.py

# Test
pytest tests/ -v
pytest --cov=src

# Run
streamlit run app.py

# Evaluate
python scripts/evaluate.py --phase all

# Tune threshold
python scripts/tune_confidence.py
```

---

## Rollback Procedures

If Phase X fails catastrophically:

**Phase 2 fails (embedding):**
- Delete `data/processed/chroma_db/`
- Retry with smaller embedding model
- Rollback to Phase 1B (ingestion still works)

**Phase 5 fails (RAG):**
- Revert `src/rag_chain.py` to empty template
- Fix issues step-by-step
- Rollback to Phase 4.5 (retrieval still works)

**Phase 8 fails (tests):**
- Don't ship, fix tests first
- Debug individual test failures
- Rollback to Phase 7 (UI still works)

---

## Metrics Tracking

Track these during build:

| Phase | Metric | Target | Actual |
|-------|--------|--------|--------|
| 1B | Chunks created | 200-600 | 949 |
| 2 | Embedding time | <5min | ? |
| 4.5 | Retrieval pass rate | 90%+ | ? |
| 6 | Optimal F1 | ≥0.85 | ? |
| 8 | Test coverage | 80%+ | ? |
| 10 | Fresh install time | <30min | ? |

---

## When You're Done

1. Tag v1.0: `git tag -a v1.0 -m "MVP launch"`
2. Push to remote: `git push origin --tags`
3. Create GitHub release with summary
4. Document lessons learned in IMPROVEMENT_ROADMAP.md
5. Start v1.1 backlog

---

**Next Step:** Phase 2 - Build vector store  
**Time:** ~2 hours  
**Command:** `python scripts/build_index.py`
