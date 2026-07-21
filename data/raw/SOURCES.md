# RedundancyAI — Fair Work Document Registry

**Last Verified:** 21 July 2026  
**Next Review:** 21 October 2026 (Quarterly)

---

## Active Documents (v1)

Documents are locked for v1. Updates only quarterly.

### 1. FWO Redundancy Pay Factsheet
- **URL:** https://www.fairwork.gov.au/documents-and-publications/fact-sheets-and-templates/fact-sheets/minimum-wages-and-conditions/redundancy-pay
- **Filename:** `fwo_redundancy_pay.pdf`
- **Status:** ⏳ To be downloaded
- **Size (approx):** 500 KB
- **Scope:** Redundancy pay rates by years of service (full-time + part-time)
- **Checksum (SHA-256):** [Generated on first download]
- **Downloaded:** [Pending]
- **Update Frequency:** Quarterly
- **Critical for:** Core FAQ — "How much redundancy pay?"
- **Notes:** Source of truth for redundancy calculations. Contains tables by years of service (2-10+ years).

### 2. National Employment Standards (NES) Summary
- **URL:** https://www.fairwork.gov.au/workplace-rights/national-employment-standards
- **Filename:** `nes_summary.pdf`
- **Status:** ⏳ To be downloaded
- **Size (approx):** 300 KB
- **Scope:** 10 NES, notice period definitions, leave entitlements
- **Checksum (SHA-256):** [Generated on first download]
- **Downloaded:** [Pending]
- **Update Frequency:** Annually (rarely changes)
- **Critical for:** Notice periods, leave entitlements, eligible employee definitions
- **Notes:** Legislative reference document. Contains definitions of redundancy, notice, leave.

### 3. Fair Work Act — Redundancy Section (Section 122A-122B)
- **URL:** https://www.legislation.gov.au/C2009A00001/latest/text
- **Filename:** `fair_work_act_excerpt.txt`
- **Status:** ⏳ To be downloaded
- **Size (approx):** 50 KB (excerpt only)
- **Scope:** Legal definition of redundancy, eligibility criteria
- **Checksum (SHA-256):** [Generated on first download]
- **Downloaded:** [Pending]
- **Update Frequency:** Annually (legislative changes rare)
- **Critical for:** Legal definitions, eligibility verification
- **Notes:** Extract Sections 122A-122B only (redundancy). Full Fair Work Act is too large; use excerpt.

### 4. Unpaid Entitlements Guide
- **URL:** https://www.fairwork.gov.au/documents-and-publications/fact-sheets-and-templates/fact-sheets/entitlements/unpaid-entitlements
- **Filename:** `unpaid_entitlements.pdf`
- **Status:** ⏳ To be downloaded
- **Size (approx):** 300 KB
- **Scope:** Annual leave, long service leave, unpaid leave calculations
- **Checksum (SHA-256):** [Generated on first download]
- **Downloaded:** [Pending]
- **Update Frequency:** Quarterly
- **Critical for:** "What about my unused leave?"
- **Notes:** Covers leave accrual, payment on termination, part-time adjustments.

### 5. Modern Awards — Summary Table
- **URL:** https://www.fairwork.gov.au/awards-and-agreements/awards/minimum-wages-and-conditions-found-in-awards
- **Filename:** `awards_summary.csv`
- **Status:** ⏳ To be downloaded
- **Size (approx):** 100 KB
- **Scope:** Award-minimum entitlements by industry (condensed, not full award text)
- **Checksum (SHA-256):** [Generated on first download]
- **Downloaded:** [Pending]
- **Update Frequency:** Quarterly (minimum wages update often)
- **Critical for:** Award-specific context
- **Notes:** Simplified reference. Links to full awards but doesn't include full text (too large).

---

## Deprecated Documents

(None yet for v1)

---

## How to Update This Registry

When refreshing documents (quarterly):

1. **Download:** Get latest from URLs above
2. **Save:** `data/raw/[filename]`
3. **Checksum:** Compute SHA-256, update registry
4. **Update:** Change "Downloaded: [date]"
5. **Rebuild:** `python scripts/build_index.py`
6. **Commit:** `git add . && git commit -m "Refresh Fair Work docs: [date]"`
7. **Document:** Update CHANGELOG.md

---

## Scope Lock (v1 Only)

- **5 documents locked** — No additions to v1 without approval
- **No unfair dismissal** — Different legal framework, v1.1+
- **No award-specific deep-dives** — Summary only for v1
- **No multi-jurisdiction** — Australia only for v1

Future versions can add NZ, unfair dismissal, award deep-dives, etc.

---

## Download Script

See `scripts/download_sources.py` for automated download with:
- URL verification
- File size validation
- SHA-256 checksum computation
- Registry auto-update
- Error handling + retry logic

---

**Last updated:** 21 July 2026 by Initial Setup
