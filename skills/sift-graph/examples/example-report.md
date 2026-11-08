# SIFT-Graph Report: sfl-compiler PassTwoEngine Concurrency

**Generated**: 2026-07-04T12:00:00Z  
**Project**: home-b08x-WorkspaceV3-sfl-compiler  
**Graph Status**: indexed (940,641 nodes, 949,484 edges)  
**Producer**: sift-graph v0.1  
**Query**: "PassTwoEngine concurrency constraints"

---

## 1. ✅ Verified Facts

- **PassTwoEngine#annotate_interpersonal uses a circuit breaker with max_retries=3**
  - Credibility: 5/5
  - Provenance: [Method](home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate_interpersonal:95-122)
  <!-- SIFT-GRAPH: {"claim_id": "a1b2c3d4", "text": "PassTwoEngine#annotate_interpersonal uses a circuit breaker with max_retries=3", "provenance": {"project": "home-b08x-WorkspaceV3-sfl-compiler", "node_type": "Method", "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate_interpersonal", "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb", "start_line": 95, "end_line": 122, "evidence_type": "SourceCode"}, "credibility": 5, "evidence_type": "SourceCode", "section": "Verified Facts"} -->

- **PassTwoEngine#annotate calls DerivationHash.compute for every clause**
  - Credibility: 5/5
  - Provenance: [Edge:CALLS](home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate -> home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.types.DerivationHash.compute:31-82)
  <!-- SIFT-GRAPH: {"claim_id": "e5f6g7h8", "text": "PassTwoEngine#annotate calls DerivationHash.compute for every clause", "provenance": {"project": "home-b08x-WorkspaceV3-sfl-compiler", "node_type": "Edge", "edge_type": "CALLS", "edge_source": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate", "edge_target": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.types.DerivationHash.compute", "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb", "start_line": 31, "end_line": 82, "evidence_type": "SourceCode"}, "credibility": 5, "evidence_type": "SourceCode", "section": "Verified Facts"} -->

- **PassTwoEngine uses a per-chunk timeout of 120s (lowered from 180s after observing p95=90s)**
  - Credibility: 4/5
  - Provenance: [Method](home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.initialize:20-24)
  <!-- SIFT-GRAPH: {"claim_id": "i9j0k1l2", "text": "PassTwoEngine uses a per-chunk timeout of 120s (lowered from 180s after observing p95=90s)", "provenance": {"project": "home-b08x-WorkspaceV3-sfl-compiler", "node_type": "Method", "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.initialize", "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb", "start_line": 20, "end_line": 24, "evidence_type": "SourceCode"}, "credibility": 4, "evidence_type": "SourceCode", "section": "Verified Facts"} -->

- **DerivationHash.compute produces a SHA256 hash of premises + inference_rule + conclusion**
  - Credibility: 5/5
  - Provenance: [Function](home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.types.DerivationHash.compute:440-455)
  <!-- SIFT-GRAPH: {"claim_id": "m3n4o5p6", "text": "DerivationHash.compute produces a SHA256 hash of premises + inference_rule + conclusion", "provenance": {"project": "home-b08x-WorkspaceV3-sfl-compiler", "node_type": "Function", "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.types.DerivationHash.compute", "file_path": "lib/sfl/compiler/types.rb", "start_line": 440, "end_line": 455, "evidence_type": "SourceCode"}, "credibility": 5, "evidence_type": "SourceCode", "section": "Verified Facts"} -->

---

## 2. ⚠️ Errors and Corrections

- **Claim that PassTwoEngine uses Thread.new for parallelism is FALSE**
  - Credibility: 1/5
  - Provenance: [Comment](home-b08x-WorkspaceV3-sfl-compiler.lib.sfl/compiler/pass_two/pass_two_engine.rb:1-5)
  - Correction: PassTwoEngine uses a circuit breaker pattern, not Thread.new. The actual concurrency constraint is PyCall's single-thread limit (from the seishun review).
  <!-- SIFT-GRAPH: {"claim_id": "q7r8s9t0", "text": "Claim that PassTwoEngine uses Thread.new for parallelism is FALSE", "provenance": {"project": "home-b08x-WorkspaceV3-sfl-compiler", "node_type": "Comment", "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.rb", "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb", "start_line": 1, "end_line": 5, "evidence_type": "SourceCode"}, "credibility": 1, "evidence_type": "SourceCode", "section": "Errors and Corrections"} -->

---

## 3. 🛠️ Corrections Summary

The initial assumption that PassTwoEngine uses Thread.new was incorrect. The actual concurrency model uses circuit breakers with retries, and the real constraint is PyCall's single-thread limit (documented in the seishun review, not in this codebase).

---

## 4. 📌 Potential Leads

- **PyCall single-thread limit** — This is the actual concurrency constraint for Ruby-Python interop. Not documented in sfl-compiler itself; see seishun review.
  - Credibility: 3/5
  - Provenance: [ExternalSource](https://github.com/seishun/sift-review-2026-06)
  <!-- SIFT-GRAPH: {"claim_id": "u1v2w3x4", "text": "PyCall single-thread limit is the actual concurrency constraint", "provenance": {"project": "N/A", "node_type": "ExternalSource", "qualified_name": "https://github.com/seishun/sift-review-2026-06", "file_path": "https://github.com/seishun/sift-review-2026-06", "start_line": 0, "end_line": 0, "evidence_type": "ExternalSource"}, "credibility": 3, "evidence_type": "ExternalSource", "section": "Potential Leads"} -->

---

## 5. 🔴 Assessment of Source Reliability

| Source | Usefulness | Notes | Rating |
|--------|------------|-------|--------|
| lib/sfl/compiler/pass_two/pass_two_engine.rb | High | Primary source for PassTwoEngine behavior | 5 |
| lib/sfl/compiler/types.rb | High | Contains DerivationHash.compute definition | 5 |
| seishun review (external) | Medium | Documents PyCall constraint, not in codebase | 3 |

---

## 6. 📜 Revised Summary (Corrected & Accurate)

PassTwoEngine in sfl-compiler uses a circuit breaker pattern with configurable retries (default 3) for its annotation methods. The `annotate` method calls `DerivationHash.compute` for every clause to produce a SHA256 hash of the reasoning trace. The per-chunk timeout was lowered from 180s to 120s after observing p95 latency of 90s. **Contrary to initial assumption, there is no Thread.new usage in PassTwoEngine.** The actual concurrency constraint for Ruby-Python interop is PyCall's single-thread limit, which is documented in the external seishun review, not in this codebase.

---

## 7. 🏆 What a Fact-Checker Might Say

**Mostly True**. The claims about PassTwoEngine's circuit breaker, DerivationHash.compute, and timeout configuration are well-supported by the codebase. The claim about Thread.new usage is false and has been corrected. The PyCall constraint is a valid observation but requires external sourcing.

---

## 8. 💡 Tip Suggestion

When analyzing concurrency in Ruby-Python interop codebases, always check for PyCall's single-thread limit. This is a well-known constraint that affects all Ruby code calling Python via PyCall, regardless of the Ruby-side concurrency patterns.

---

## 9. 📊 SIFT-Graph Meta-Rubric Scores

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Claim Provenance | 4.50 | 40% | 1.80 |
| Section Completeness | 5.00 | 25% | 1.25 |
| Severity Calibration | 4.00 | 20% | 0.80 |
| Self Critique Payoff | 3.00 | 15% | 0.45 |
| **Raw Score** | | | **4.30** |
| **Pitfall Penalty** | | | **-0.00** |
| **Final Score** | | | **4.3** |
| **Chain Integrity** | 3.00 | | (min of all dimensions) |

**Essential Cap**: Not triggered (Claim Provenance >= 3)  
**Status**: Strong — minor revisions suggested

---

## Machine-Readable Output

The full report with provenance tuples is available in JSON format:
- `home-b08x-WorkspaceV3-sfl-compiler-PassTwoEngine-concurrency.json`

Each claim in the JSON includes:
```json
{
  "claim_id": "a1b2c3d4",
  "text": "PassTwoEngine#annotate_interpersonal uses a circuit breaker with max_retries=3",
  "provenance": {
    "project": "home-b08x-WorkspaceV3-sfl-compiler",
    "node_type": "Method",
    "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate_interpersonal",
    "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
    "start_line": 95,
    "end_line": 122,
    "evidence_type": "SourceCode"
  },
  "credibility": 5,
  "evidence_type": "SourceCode",
  "section": "Verified Facts"
}
```
