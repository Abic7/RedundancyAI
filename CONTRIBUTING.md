# Contributing to RedundancyAI

## Code Style

### Formatting
```bash
black src/ tests/ scripts/  # Format code
ruff check src/             # Lint
mypy src/                   # Type checking
```

### Before PR
- [ ] `black` formatting passes
- [ ] `ruff` has no errors
- [ ] `mypy` type hints valid
- [ ] All tests pass: `pytest -v`
- [ ] Coverage ≥ 80%

## Adding a New Fair Work Document

1. **Save document to `data/raw/[filename]`**

2. **Update `data/raw/SOURCES.md`:**
   ```markdown
   ### Document Name
   - **URL:** https://source-url
   - **File:** filename.pdf
   - **Downloaded:** 2026-07-21
   - **Scope:** What it covers
   - **Notes:** Any important info
   ```

3. **Re-index:**
   ```bash
   python scripts/build_index.py
   ```

4. **Test:**
   ```bash
   pytest tests/test_retrieval.py
   ```

5. **Verify chunks:**
   ```bash
   python -c "from src.ingest import DocumentIngestionPipeline; p = DocumentIngestionPipeline(); docs = p.load_documents(); print(f'Chunks: {len(p.chunk_documents(docs))}')"
   ```

## Reporting Bugs

Create a GitHub issue with:
- **Question that failed:** (exact user query)
- **Expected answer:** (what should happen)
- **Actual response:** (what happened)
- **Confidence score:** (from response)
- **Reproduction:** (steps to reproduce)

Example:
```
Q: "How much redundancy pay after 4 years?"
Expected: "7-8 weeks pay"
Got: "I don't have reliable information about redundancy pay"
Confidence: 0.2
```

## Requesting a Feature

Create a GitHub issue with:
- **Feature:** Brief description
- **Rationale:** Why it's needed
- **Impact:** Which users benefit
- **Effort:** Low/Medium/High estimate

Example: "Multi-turn conversation support — enables follow-up questions like 'Why is that?' or 'What about X?'"

## Testing Checklist

### Unit Tests
```bash
pytest tests/test_output_processor.py -v    # Citations
pytest tests/test_ingest.py -v              # Document loading
```

### Integration Tests
```bash
pytest tests/test_rag_chain.py -v           # Full RAG pipeline
pytest tests/test_prompt_injection.py -v    # Security
```

### Golden Questions
```bash
pytest tests/test_rag_chain.py::test_golden_questions -v
```

Must pass: 25+ real-world scenarios

### Coverage
```bash
pytest --cov=src --cov-report=html
# Opens htmlcov/index.html
```

Target: ≥ 80%

## Documentation Changes

- **README.md:** Setup, usage, scope
- **BUILD.md:** Implementation phases
- **ARCHITECTURE.md:** Design decisions
- **CONTRIBUTING.md:** This file

Keep docs:
- **Brief:** Get to the point
- **Linked:** Cross-reference where relevant
- **Tested:** Examples actually work
- **Current:** Update when code changes

## Code Review Process

1. **Create PR** with clear title
2. **Automated checks:**
   - Tests pass ✓
   - Linting passes ✓
   - Coverage ≥ 80% ✓
3. **Manual review:** At least 1 approval
4. **Merge:** Squash commits, use conventional message

### PR Title Format
```
[Feature/Fix/Docs] Brief description

Examples:
- [Feature] Add multi-turn conversation support
- [Fix] Improve citation accuracy on boundary cases
- [Docs] Update README with troubleshooting section
```

### PR Description Template
```
## What
Brief description of changes

## Why
Why is this needed? (solves problem X, improves metric Y)

## How
How did you implement it?

## Testing
How did you verify it works?

## Breaking Changes
Any breaking API changes? (rarely, this is MVP)
```

## Deployment Checklist

Before v1.1 release:

- [ ] All tests passing
- [ ] Coverage ≥ 80%
- [ ] No security warnings
- [ ] README updated
- [ ] CHANGELOG.md updated
- [ ] Tag created: `git tag -a v1.1 -m "v1.1 release"`

## Questions?

See README.md for support links.
