# RedundancyAI Architecture Diagrams

This directory contains 5 comprehensive architecture diagrams for the RedundancyAI RAG chatbot system. All diagrams are in `.drawio` format and can be edited in draw.io (online or desktop).

## Diagrams

### 1. **System Architecture** (`1-system-architecture.drawio`)
**Overview:** Complete 5-layer pipeline showing how data flows through the system.

**Layers:**
- Layer 1: Data Ingestion (Orange) — Document loading, chunking, embedding, vector storage
- Layer 2: Retrieval & Safety (Blue) — User question, injection detection, similarity search, confidence gating, reranking
- Layer 3: LLM Processing (Green) — Context formatting, system prompt, LLM inference, response generation
- Layer 4: Output Validation (Purple) — Citation extraction, verification, hallucination detection
- Layer 5: User Interface (Yellow) — Streamlit chat, confidence indicators, source attribution, safety warnings

**Key Components:** 20+ components with detailed labels and flow connections.

**Use Case:** High-level understanding of the entire system architecture.

---

### 2. **Data Flow** (`2-data-flow.drawio`)
**Overview:** Step-by-step execution flow showing what happens to user input at each stage.

**Stages:**
1. User Question Input
2. Injection Defense (9 patterns)
3. Vector Store Retrieval (949 chunks)
4. Confidence Gate (threshold: 0.25)
5. Reranking (cross-encoder)
6. Context Formatting (source tags)
7. LLM Inference (Gemma-4-12B, 3-5 sec)
8. Output Validation (citation + hallucination check)

**Data Samples:** Shows example data at each stage (input tokens, retrieved chunks, LLM prompt, output validation).

**Performance Metrics:** Latency breakdown for each stage (total: 3.1-5.1 sec).

**Use Case:** Debugging, performance optimization, understanding request lifecycle.

---

### 3. **Security Defense Stack** (`3-security-layers.drawio`)
**Overview:** 6-layer security defense against prompt injection and hallucinations.

**Defense Layers:**
1. **Injection Detection** — 9 attack patterns blocked (system override, rule override, persona swap, etc.)
2. **Retrieval Isolation** — Only Fair Work documents, no external context injection
3. **Confidence Gate** — Threshold 0.25, empirically tuned, prevents false refusals
4. **System Prompt Hardening** — Citation enforcement, roleplay prevention
5. **Citation Verification** — 100% citation accuracy check post-LLM
6. **Logging & Monitoring** — Incident tracking and anomaly detection

**Defense Effectiveness:** 9/9 patterns tested ✅, 100% citation accuracy ✅, zero hallucinations ✅

**Use Case:** Security audits, compliance, understanding risk mitigation.

---

### 4. **Component Dependencies** (`4-component-dependencies.drawio`)
**Overview:** Module-level dependency graph showing how Python modules depend on each other.

**Tiers:**
- Ingestion Tier: `ingest.py`, `embed_store.py`
- Retrieval & Processing Tier: `rag_chain.py` (LCEL orchestrator), `injection_detector.py`, `prompts.py`
- Output & Validation Tier: `output_processor.py`
- External Dependencies: LangChain, Chroma, sentence-transformers, LM Studio

**Use Case:** Understanding module responsibilities, dependency management, refactoring planning.

---

### 5. **Deployment Architecture** (`5-deployment-architecture.drawio`)
**Overview:** MVP deployment topology showing user's local machine setup.

**Components:**
- **Streamlit Server** (http://localhost:8501) — Chat interface
- **RedundancyAI Application** — Python modules (RAG chain, injection detection, output processing)
- **LM Studio** (http://localhost:1234) — Local LLM inference (Gemma-4-12B)
- **Data Layer** — Raw documents, Chroma vector store (~500MB)

**Network Flow:** User → Streamlit → RedundancyAI App → LM Studio → Response

**v2.0+ Roadmap:**
- REST API (FastAPI)
- Multi-tenant database
- Cloud deployment (Docker, Kubernetes)

**Use Case:** Deployment planning, environment setup, scaling strategy.

---

## How to Use These Diagrams

### Option 1: Online (No Installation)
1. **Open in draw.io web editor:**
   - Go to https://app.diagrams.net/
   - Click File → Open → Select `.drawio` file
   - Edit and export

### Option 2: Desktop Application
1. **Install draw.io desktop:**
   - macOS: `brew install --cask drawio`
   - Windows: Download from https://github.com/jgraph/drawio-desktop/releases
   - Linux: Download `.deb`/`.rpm`

2. **Open diagrams:**
   - Double-click any `.drawio` file
   - Edit directly in the desktop app

### Option 3: Embedded Viewer (Coming Soon)
- Interactive HTML viewer with drill-down links (use `drawiohtml.py` if needed)

---

## Editing & Exporting

### Export to PNG/SVG/PDF
```bash
# If draw.io CLI is installed
drawio -x -f png -e -s 2 -o diagram-name.drawio.png diagram-name.drawio
drawio -x -f svg -e -o diagram-name.svg diagram-name.drawio
drawio -x -f pdf -e -o diagram-name.pdf diagram-name.drawio
```

### Share Editable URL
Use draw.io's "Share" feature to generate shareable links that let others view/edit diagrams.

---

## Technical Specifications

| Property | Value |
|----------|-------|
| Format | `.drawio` (XML-based) |
| Editor | draw.io (web + desktop) |
| Diagram Type | Architecture, flowchart, dependency graph |
| Total Components | 80+ shapes across 5 diagrams |
| Colors | Official color scheme (orange, blue, green, purple, yellow layers) |
| Fonts | Calibri 10pt for consistency |
| Grid | 10px grid for alignment |

---

## Related Documentation

- **ARCHITECTURE.md** — Design decisions and data flows
- **BUILD.md** — Phase-by-phase build guide
- **SECURITY_AUDIT.md** — Comprehensive security review
- **LAUNCH_CHECKLIST.md** — Pre-launch verification

---

**Last Updated:** 21 July 2026  
**Version:** MVP (v1.0)  
**Status:** Production-ready diagrams ✅
