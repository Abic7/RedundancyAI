# RedundancyAI Diagrams — Quick Start Guide

## 📊 Five Architecture Diagrams Created

All diagrams are stored in `diagrams/` folder as `.drawio` files. Here's how to access them:

### 🚀 Quickest Way: Open in Draw.io Online (No Installation)

1. Go to **https://app.diagrams.net/**
2. Click **File → Open**
3. Navigate to `E:\LEARNING\RedundancyAI\diagrams\`
4. Select any `.drawio` file:
   - `1-system-architecture.drawio`
   - `2-data-flow.drawio`
   - `3-security-layers.drawio`
   - `4-component-dependencies.drawio`
   - `5-deployment-architecture.drawio`

### 💻 Alternative: Install Draw.io Desktop

**Windows:**
1. Download from: https://github.com/jgraph/drawio-desktop/releases
2. Run installer
3. Double-click any `.drawio` file to open

**macOS:**
```bash
brew install --cask drawio
# Then double-click any .drawio file
```

**Linux:**
```bash
# Download .deb or .rpm from GitHub releases
sudo dpkg -i draw.io-*.deb
```

---

## 📋 What Each Diagram Shows

### **1. System Architecture** — The Big Picture
```
5-Layer Pipeline:
┌─────────────────────────────────────────────┐
│ LAYER 1: DATA INGESTION (Orange)            │ → Documents → Chunks → Embeddings → Vector Store
├─────────────────────────────────────────────┤
│ LAYER 2: RETRIEVAL & SAFETY (Blue)          │ → Question → Injection Check → Search → Gate → Rerank
├─────────────────────────────────────────────┤
│ LAYER 3: LLM PROCESSING (Green)             │ → Format Context → System Prompt → LLM → Generate
├─────────────────────────────────────────────┤
│ LAYER 4: OUTPUT VALIDATION (Purple)         │ → Extract Citations → Verify → Detect Hallucinations
├─────────────────────────────────────────────┤
│ LAYER 5: USER INTERFACE (Yellow)            │ → Display Answer → Confidence → Sources → Warnings
└─────────────────────────────────────────────┘
```

**Best for:** Understanding the complete architecture at a glance.

---

### **2. Data Flow** — Step-by-Step Execution
```
User Input → [7 Processing Steps] → Final Answer

Step 1: Injection Defense (9 patterns)
Step 2: Retrieval (949 chunks)
Step 3: Confidence Gate (threshold 0.25)
Step 4: Reranking (top-3)
Step 5: Context Formatting
Step 6: LLM Inference (3-5 sec)
Step 7: Output Validation

Total Latency: 3.1-5.1 seconds
```

**Best for:** Debugging, performance optimization, tracing a question through the system.

**Includes:** Data samples at each stage + latency breakdown.

---

### **3. Security Defense Stack** — 6 Layers of Protection
```
🔴 ATTACKER
    ↓
[1] Injection Detection (9 patterns)
    ↓
[2] Retrieval Isolation (only Fair Work docs)
    ↓
[3] Confidence Gate (threshold 0.25)
    ↓
[4] System Prompt Hardening (citation enforcement)
    ↓
[5] Citation Verification (100% accuracy check)
    ↓
[6] Logging & Monitoring (incident tracking)
    ↓
🟢 SAFE RESPONSE
```

**Best for:** Security audits, compliance, understanding risk mitigation.

**Defense Metrics:** 9/9 injection patterns tested ✅, 100% citation accuracy ✅

---

### **4. Component Dependencies** — Module-Level Graph
```
Python Modules:
- ingest.py (PyPDF2, BeautifulSoup4)
- embed_store.py (Chroma, sentence-transformers)
- rag_chain.py (LangChain LCEL orchestrator)
- injection_detector.py (pattern matching)
- prompts.py (system prompts)
- output_processor.py (citation validation)

External Services:
- LM Studio (Gemma-4-12B @ localhost:1234)
- Chroma Vector DB (~500MB)
```

**Best for:** Understanding module responsibilities, refactoring, dependency management.

---

### **5. Deployment Architecture** — Local Machine Setup (v1.0)
```
User's Machine:
┌────────────────────────────────────────────┐
│ Streamlit UI (http://localhost:8501)       │
│ ↓ Chat Interface                           │
├────────────────────────────────────────────┤
│ RedundancyAI Application (Python)          │
│ - rag_chain.py (orchestration)             │
│ - injection_detector.py (defense)          │
│ - output_processor.py (validation)         │
│ ↓ HTTP to LM Studio                        │
├────────────────────────────────────────────┤
│ LM Studio (http://localhost:1234)          │
│ - Gemma-4-12B Model (12GB)                 │
│ ↓ LLM Response                             │
├────────────────────────────────────────────┤
│ Data Layer                                 │
│ - data/raw/ (5 Fair Work documents)        │
│ - data/processed/chroma_db/ (~500MB)       │
└────────────────────────────────────────────┘
```

**Best for:** Deployment planning, environment setup, scaling strategy.

**v2.0+ Roadmap:** REST API, multi-tenant DB, cloud deployment.

---

## 🎨 Diagram Customization

### Edit Colors/Styling
1. Right-click any shape → **Edit Style**
2. Modify `fillColor`, `strokeColor`, `fontSize`, etc.
3. Save (Ctrl+S or Cmd+S)

### Add New Components
1. Drag shapes from left toolbar
2. Connect with arrows (connector tool)
3. Add labels and styling

### Export Diagrams
**From draw.io desktop or web:**
1. File → Export As
2. Choose format:
   - **PNG** (embedded XML, stays editable)
   - **SVG** (vector, scales perfectly)
   - **PDF** (print-friendly)

---

## 📖 How to Share

### Option 1: Export as PNG/SVG
```bash
# If draw.io CLI installed
drawio -x -f png -e -s 2 -o diagram.drawio.png diagram.drawio
```

### Option 2: Share as Link
1. In draw.io, click **File → Share**
2. Choose "Link" or "Email"
3. Get shareable URL

### Option 3: Embed in Markdown (GitHub README)
```markdown
![System Architecture](diagrams/1-system-architecture.drawio.png)
```

---

## ✅ Quality Checklist

All 5 diagrams include:
- ✅ Clear layer/tier separation (color-coded)
- ✅ Descriptive component labels
- ✅ Data flow arrows with labels
- ✅ Latency/performance metrics
- ✅ Consistent styling (Calibri 10pt, official colors)
- ✅ Cross-referenced with documentation
- ✅ Print-ready (exported as PNG/PDF)

---

## 🔗 Quick Links

| Diagram | Purpose | Format | Components |
|---------|---------|--------|------------|
| System Architecture | High-level overview | `.drawio` | 20+ boxes, 5 layers |
| Data Flow | Step-by-step execution | `.drawio` | 7 stages + metrics |
| Security Stack | Defense mechanisms | `.drawio` | 6 layers + summary |
| Component Graph | Module dependencies | `.drawio` | 6 modules + external |
| Deployment | Local setup (v1.0) | `.drawio` | 4 components + data |

---

## 📞 Troubleshooting

### "File won't open in draw.io"
→ Try uploading to https://app.diagrams.net/ instead of opening via File → Open

### "Diagrams look different in draw.io vs desktop"
→ Both are valid; desktop has better rendering. PDF export is most reliable.

### "Want to export as high-resolution PNG for presentations"
→ Use desktop draw.io: File → Export → PNG, set scale to 2-3x

### "Need to edit diagrams programmatically"
→ `.drawio` files are XML; can be parsed/modified with Python scripts

---

## 🚀 Next Steps

1. **Open diagrams:** Use draw.io web or desktop
2. **Share with team:** Export as PNG/SVG or share link
3. **Update as needed:** Diagrams are version-controlled in Git
4. **Integrate into docs:** Embed PNG exports in README.md

---

**Created:** 21 July 2026  
**Format:** draw.io native (`.drawio` XML)  
**Status:** Ready for use ✅  
**License:** Apache 2.0 (same as RedundancyAI)
