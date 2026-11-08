---
name: sift-graph
description: "Graph-verified SIFT protocol. Replaces the static SIFT prompt with a producer that MUST query the codebase-memory knowledge graph for every claim. Every claim carries a provenance tuple (project, node_type, qualified_name, file_path, start_line, end_line, evidence_type). No claim without a tuple. No tuple without a graph hit. Designed to eliminate the 'pattern-match-from-listing' failure mode."
compatibility: ">=0.1.0"
allowed-tools: "read grep mcp_codebase_memory_mcp_list_projects mcp_codebase_memory_mcp_index_repository mcp_codebase_memory_mcp_index_status mcp_codebase_memory_mcp_get_graph_schema mcp_codebase_memory_mcp_search_graph mcp_codebase_memory_mcp_get_code_snippet mcp_codebase_memory_mcp_trace_path mcp_codebase_memory_mcp_query_graph mcp_codebase_memory_mcp_detect_changes"
metadata:
  user-invocable: "true"
  argument-hint: "<project_name> <query_or_topic>"
---

# SIFT-Graph: Graph-Verified Software/Systems Analysis

**Status**: v0.1 Design  
**Author**: b08x (with Hermes)  
**Date**: 2026-07-04  
**Supersedes**: Static SIFT prompt (`~/Documents/sift.md` v2)  

---

## TL;DR — The One Rule

> Every factual claim in a SIFT-Graph report MUST carry a provenance tuple that resolves to a node or edge in the codebase-memory knowledge graph. If the tuple does not resolve, the claim is **invalid** and the report fails the Essential Cap.

This single rule eliminates the failure mode demonstrated in the 2026-07-04 session: confident pattern-matched claims from real-but-partial context (real filenames, real class names, fabricated behavior).

---

## Why This Skill Exists

The static SIFT prompt (`~/Documents/sift.md`) is a **text-only protocol**. It produces plausible-looking reports with:
- Real file names (from directory listings)
- Real class/function names (from grep or memory)
- Fabricated behavioral claims (pattern-matched from the names)

The [memory_research SIFT report](~/Documents/memory_research/SIFT_Report_Full_Check_2026-03-04.md) is a worked example of this failure:
- Every Confidence column reads "4-5" (no variation)
- Every source gets "✅ High / 4-5" (no differentiation)
- The "Unable to Substantiate" claims are indistinguishable from the "✅ Correct" claims in terms of evidence quality

**Root cause**: The static prompt has no access to ground truth. It cannot verify whether a file was actually opened, whether a function was actually read, or whether a claim is supported by the code.

**Solution**: Replace the static prompt with a **graph-verified producer**. The codebase-memory MCP tool provides a knowledge graph of the target codebase (functions, classes, call edges, file paths, line ranges). Every claim must carry a provenance tuple that resolves to a node/edge in that graph. If it doesn't resolve, the claim is invalid.

---

## Failure Modes This Design Catches

| Failure Mode | Static SIFT Behavior | SIFT-Graph Mitigation |
|--------------|----------------------|------------------------|
| Pattern-match-from-listing | Names real files/classes, fabricates behavior | Provenance tuple must resolve to graph node/edge. Fabricated claims have no tuple. |
| Section-skipping | Drops sections under context pressure | Audit pass counts claims per section. Missing sections = missing claims = lower provenance coverage. |
| Severity drift | Early "5 (critical)" becomes baseline; later issues deflate | Each claim carries its own credibility score + evidence_type. Distributional stats catch drift. |
| Self-critique theater | Critique step produces plausible gaps that don't change the report | Treat critique as a second claim ledger. Diff pre/post. Empty diff = theater. |

---

## Architecture

### 0. Precondition: Indexed Codebase

SIFT-Graph requires the target codebase to be indexed in the codebase-memory knowledge graph. If not already indexed:

```bash
# Index a new codebase (full mode for first-time, moderate for updates)
mcp_codebase_memory_mcp_index_repository \
  repo_path=/path/to/codebase \
  mode=full \
  persistence=true

# Check status
mcp_codebase_memory_mcp_index_status project=codebase-name
```

The `persistence=true` flag writes a compressed artifact to `.codebase-memory/graph.db.zst` that can be shared with teammates (they can bootstrap from the artifact instead of full re-indexing).

### 1. Pipeline Stages

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Context Input   │────▶│  Graph Query    │────▶│ Claim Generation│
│  (user query)    │     │  (provenance)    │     │  (with tuples)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Provenance Audit │◀────│  Claim Ledger    │◀────│  Self-Critique   │
│  (tuple → graph) │     │  (all claims)    │     │  (2nd ledger)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  Report Assembly │
                                                 │  (8-section +   │
                                                 │   provenance)   │
                                                 └─────────────────┘
```

#### Stage 1: Context Input
- Accepts: a user query (free-form) or a structured topic
- Normalizes: extracts key terms, identifies target project
- Validates: checks project is indexed; if not, triggers indexing

#### Stage 2: Graph Query
- For each key term, queries the codebase-memory graph:
  - `search_graph(query=term, label=Function)` — find functions
  - `search_graph(query=term, label=Class)` — find classes
  - `search_graph(query=term, label=File)` — find files
  - `trace_path(function_name=X, direction=both, depth=2)` — find callers/callees
- Returns: a list of candidate nodes/edges with metadata (qualified_name, file_path, start_line, end_line, complexity, etc.)

#### Stage 3: Claim Generation
- For each candidate node/edge, generates **at most one claim** (density over completeness)
- Each claim MUST include a provenance tuple:
  ```json
  {
    "claim_id": "uuid",
    "text": "PassTwoEngine.annotate_interpersonal uses a circuit breaker with 3 retries",
    "provenance": {
      "project": "home-b08x-WorkspaceV3-sfl-compiler",
      "node_type": "Method",
      "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate_interpersonal",
      "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
      "start_line": 95,
      "end_line": 122,
      "evidence_type": "SourceCode",
      "snippet": "...actual lines 95-122..."
    },
    "credibility": 4,
    "evidence_type": "SourceCode",
    "section": "Verified Facts"
  }
  ```
- **Rule**: No claim enters the ledger without a provenance tuple that resolves to a graph node/edge.

#### Stage 4: Provenance Audit
- For each claim in the ledger, re-queries the graph to verify the provenance tuple exists
- Computes **provenance_coverage** = (claims_with_valid_provenance / total_claims)
- If provenance_coverage < 0.5, triggers **Essential Cap** (final score capped at 2.0)

#### Stage 5: Self-Critique
- Runs a second pass: "What claims are missing? What evidence is weak?"
- Produces a **critique ledger** with its own provenance tuples
- Computes **critique_payoff** = (new_claims_added / total_claims)
  - If critique_payoff ≈ 0, the critique was theater

#### Stage 6: Report Assembly
- Groups claims by section (Verified Facts, Errors & Corrections, Potential Leads, etc.)
- Formats as 8-section SIFT report (compatible with existing consumers)
- Embeds machine-readable provenance annotations (for audit pass)

---

## Provenance Tuple Format

A provenance tuple is a JSON object with the following fields:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| project | string | codebase-memory project name (e.g., "home-b08x-WorkspaceV3-sfl-compiler") | Yes |
| node_type | string | One of: Function, Method, Class, Variable, File, Module, Section, Folder, Route | Yes |
| qualified_name | string | Full qualified name from the graph (e.g., "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate") | Yes |
| file_path | string | Absolute or project-relative file path | Yes |
| start_line | integer | 1-indexed start line | Yes |
| end_line | integer | 1-indexed end line | Yes |
| evidence_type | string | One of: SourceCode, Documentation, Test, Config, Comment, ExternalSource | Yes |
| snippet | string | The actual text from start_line to end_line (optional, for human review) | No |
| edge_type | string | If provenance is an edge, the edge type (CALLS, IMPORTS, etc.) | No |
| edge_source | string | If provenance is an edge, the source node qualified_name | No |
| edge_target | string | If provenance is an edge, the target node qualified_name | No |

### Example Tuples

**Function provenance:**
```json
{
  "project": "home-b08x-WorkspaceV3-sfl-compiler",
  "node_type": "Function",
  "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.compute_derivation_hash",
  "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
  "start_line": 440,
  "end_line": 455,
  "evidence_type": "SourceCode"
}
```

**Call edge provenance:**
```json
{
  "project": "home-b08x-WorkspaceV3-sfl-compiler",
  "node_type": "Edge",
  "edge_type": "CALLS",
  "edge_source": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate",
  "edge_target": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.compute_derivation_hash",
  "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
  "start_line": 31,
  "end_line": 82,
  "evidence_type": "SourceCode"
}
```

---

## SIFT-Graph Meta-Rubric

The meta-rubric scores SIFT-Graph reports (or any SIFT report) against four dimensions + one derived integrity score. It is modeled on the [rubysmithing scoring algorithm](~/Documents/deepwiki-builder/output/syncopated-context001/markdown/13-QA-Pipeline-SIFT-Protocol-Diagnostics/12-Scoring-Algorithm.md) (Weighted Sum + Pitfall Penalty + Essential Cap).

### Dimensions (Weighted)

| Dimension | Weight | Description | Scoring |
|-----------|--------|-------------|---------|
| **Claim Provenance** | 40% | Fraction of claims with valid provenance tuples that resolve to the graph | 1-5: <50%=1, 50-70%=2, 70-85%=3, 85-95%=4, ≥95%=5 |
| **Section Completeness** | 25% | All 8 SIFT sections present with ≥1 claim each | 1-5: 0-2 sections=1, 3-4=2, 5-6=3, 7=4, 8=5 |
| **Severity Calibration** | 20% | Distribution of credibility scores (1-5) — variance and mean | 1-5: std_dev > 1.5=1, 1.0-1.5=2, 0.5-1.0=3, 0.2-0.5=4, <0.2=5 |
| **Self-Critique Payoff** | 15% | Fraction of critique-ledger claims that were NOT in the original ledger | 1-5: 0%=1, 1-10%=2, 11-25%=3, 26-50%=4, >50%=5 |

### Derived Score: Chain Integrity

**Chain Integrity** = min(Claim Provenance, Section Completeness, Severity Calibration, Self-Critique Payoff)

This penalizes reports where multiple dimensions fail together (indicating a systemic failure, not isolated issues).

### Essential Cap

If **Claim Provenance < 3** (i.e., < 70% of claims have valid provenance), the **final score is capped at 2.0**, regardless of other dimension scores.

This is the "load-bearing" rule: a report with poor provenance is unreliable, no matter how well it scores on other dimensions.

### Pitfall Penalty

For each **anti-pattern** detected in the report, subtract 0.3 from the final score (before capping). Anti-patterns include:
- Claim with provenance tuple that does NOT resolve to the graph (-0.3)
- Claim with evidence_type not in the allowed enum (-0.3)
- Section with 0 claims (-0.3 per missing section)
- Credibility score outside 1-5 range (-0.3)

### Final Score Calculation

```
raw_score = (
  (claim_provenance_score * 0.40) +
  (section_completeness_score * 0.25) +
  (severity_calibration_score * 0.20) +
  (self_critique_payoff_score * 0.15)
)

final_score = max(0, raw_score - (pitfall_count * 0.3))
final_score = min(final_score, 2.0) if claim_provenance_score < 3 else final_score
final_score = round(final_score, 1)
```

### Score Interpretation

| Score | Interpretation | Action |
|-------|----------------|--------|
| 5.0 | Exemplary | Publish as-is |
| 4.0-4.9 | Strong | Minor revisions |
| 3.0-3.9 | Adequate | Review for gaps |
| 2.0-2.9 | Marginal | Significant revisions needed |
| < 2.0 | Unreliable | Do not trust; re-run with stricter provenance |

---

## Output Format

SIFT-Graph produces a **superset** of the 8-section SIFT report format, with two additions:

1. **Machine-readable provenance annotations** (JSON, embedded in HTML comments or a separate `.sift-graph.json` file)
2. **Meta-rubric scores** (appended as a 9th section)

### Example Output (Markdown + JSON)

```markdown
# SIFT-Graph Report: sfl-compiler Pass 2 Concurrency

**Generated**: 2026-07-04T12:00:00Z  
**Project**: home-b08x-WorkspaceV3-sfl-compiler  
**Graph Status**: indexed (940,641 nodes, 949,484 edges)  
**Producer**: sift-graph v0.1  

---

## 1. ✅ Verified Facts

| Statement | Status | Provenance | Confidence |
|-----------|--------|------------|------------|
| PassTwoEngine uses a circuit breaker with 3 retries in annotate_interpersonal | ✅ | [Graph:Method](home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate_interpersonal:95-122) | 5 |

<!-- SIFT-GRAPH: {"claim_id": "abc123", "provenance": {"project": "home-b08x-WorkspaceV3-sfl-compiler", "node_type": "Method", "qualified_name": "...annotate_interpersonal", "file_path": ".../pass_two_engine.rb", "start_line": 95, "end_line": 122, "evidence_type": "SourceCode"}} -->

---

## 9. 📊 SIFT-Graph Meta-Rubric Scores

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Claim Provenance | 5 | 40% | 2.0 |
| Section Completeness | 5 | 25% | 1.25 |
| Severity Calibration | 4 | 20% | 0.8 |
| Self-Critique Payoff | 3 | 15% | 0.45 |
| **Raw Score** | | | **4.50** |
| Pitfall Penalty | | | -0.0 |
| **Final Score** | | | **4.5** |
| Chain Integrity | 3 | | (min of all dimensions) |

**Essential Cap**: Not triggered (Claim Provenance ≥ 3)  
**Status**: Strong — minor revisions suggested
```

---

## Implementation Notes

### Minimal Python Producer (sift_graph.py)

See [scripts/sift_graph.py](scripts/sift_graph.py) for a reference implementation (~200 lines).

Key functions:
- `index_if_needed(project_name, repo_path)` — ensures the codebase is indexed
- `query_graph_for_term(project, term)` — returns candidate nodes/edges
- `generate_claims(candidates)` — produces claims with provenance tuples
- `audit_provenance(claims, project)` — verifies tuples against the graph
- `assemble_report(claims, critique_claims)` — formats the 8-section report
- `score_report(claims, critique_claims)` — computes meta-rubric scores

### Dependencies

- **codebase-memory MCP server** — provides the knowledge graph
- **Python 3.11+** — for the reference implementation
- **pydantic** — for claim/provenance tuple validation (optional but recommended)
- **pyyaml** — for rubric config loading (optional)

### Performance

- Indexing: ~1-2 minutes for sfl-compiler (940k nodes) on first run; ~10-30 seconds for updates
- Query: ~50-200ms per `search_graph` call; ~100-500ms per `trace_path` call
- Typical report: 20-50 claims → 20-50 graph queries → 2-5 seconds total

### Limitations

1. **Graph must be indexed** — SIFT-Graph cannot run on unindexed codebases
2. **Provenance tuples are brittle** — if the graph schema changes, tuples may break
3. **No cross-repo claims** — the graph is per-repo; claims about "Project A calls Project B" require cross-repo indexing (use `mode=cross-repo-intelligence`)
4. **External sources** — claims about external docs (Harvard Health, NIH) cannot be verified against the codebase graph; use evidence_type="ExternalSource" and manual review

---

## Migration Path from Static SIFT

1. **Keep the static prompt** for non-codebase targets (research papers, general knowledge)
2. **Use SIFT-Graph** for codebase analysis (the primary use case you named)
3. **Add a fallback** — if the codebase is not indexed, fall back to static SIFT with a warning
4. **Calibrate** — run both on the same target, compare outputs, tune the rubric

---

## Related Artifacts

- [Static SIFT prompt v2](~/Documents/sift.md) — the protocol this replaces for codebase analysis
- [memory_research SIFT report](~/Documents/memory_research/SIFT_Report_Full_Check_2026-03-04.md) — worked example of static SIFT failure mode
- [rubysmithing scoring algorithm](~/Documents/deepwiki-builder/output/syncopated-context001/markdown/13-QA-Pipeline-SIFT-Protocol-Diagnostics/12-Scoring-Algorithm.md) — precedent for Weighted Sum + Pitfall Penalty + Essential Cap
- [codebase-memory skill](~/.syncopated/skills/codebase-memory/SKILL.md) — the knowledge graph tool this skill depends on
- sfl-compiler codebase-memory project (`home-b08x-WorkspaceV3-sfl-compiler`) — 940k nodes, 949k edges
- sfl_geb_compiler_v1 codebase-memory project (`home-b08x-WorkspaceV3-crews-sfl_geb_compiler_v1_crewai-project`) — 159 nodes, 239 edges

---

## Open Questions

1. **Cross-repo provenance** — How to handle claims about interactions between projects? Use `mode=cross-repo-intelligence` and the `target_projects` param.
2. **External source verification** — Should SIFT-Graph attempt to verify ExternalSource claims (e.g., by fetching the URL)? Or leave that to a separate pass?
3. **Caching provenance tuples** — Should resolved tuples be cached to avoid re-querying the graph for the same claim in future runs?
4. **Human review integration** — How to surface provenance tuples to a human reviewer? Embed in markdown? Separate JSON file? Both?

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v0.1 | 2026-07-04 | b08x | Initial design. Replaces static SIFT prompt with graph-verified producer. |
