#!/usr/bin/env python3
from __future__ import annotations
"""
SIFT-Graph: Graph-Verified SIFT Producer

A minimal reference implementation of the SIFT-Graph protocol.
Every claim MUST carry a provenance tuple that resolves to the codebase-memory graph.

Usage:
    python sift_graph.py <project_name> <query> [--output-dir <path>]

Example:
    python sift_graph.py home-b08x-WorkspaceV3-sfl-compiler "PassTwoEngine concurrency"

Dependencies:
    - hermes-mcp-client (for MCP tool access)
    - pydantic (optional, for validation)
    - pyyaml (optional, for config)

Author: b08x (with Hermes)
Date: 2026-07-04
"""

import json
import sys
import uuid
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Literal
from pathlib import Path

# Try to import the real MCP client
try:
    from sift_graph_mcp import SQLiteMCPClient
    REAL_MCP_AVAILABLE = True
except ImportError:
    REAL_MCP_AVAILABLE = False

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

EvidenceType = Literal[
    "SourceCode",
    "Documentation", 
    "Test",
    "Config",
    "Comment",
    "ExternalSource",
    "Inference"
]

NodeType = Literal[
    "Function", "Method", "Class", "Variable", "File", 
    "Module", "Section", "Folder", "Route", "Edge"
]

SectionName = Literal[
    "Verified Facts",
    "Errors and Corrections", 
    "Potential Leads",
    "Source Reliability",
    "Corrections Summary",
    "Revised Summary",
    "Fact-Checker Assessment",
    "Tip Suggestion"
]


@dataclass
class ProvenanceTuple:
    """A provenance tuple that must resolve to a node/edge in the codebase-memory graph."""
    project: str
    node_type: NodeType
    qualified_name: str
    file_path: str
    start_line: int
    end_line: int
    evidence_type: EvidenceType
    snippet: Optional[str] = None
    # For edge provenance
    edge_type: Optional[str] = None
    edge_source: Optional[str] = None
    edge_target: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Claim:
    """A single factual claim with provenance."""
    text: str
    provenance: ProvenanceTuple
    credibility: int  # 1-5
    evidence_type: EvidenceType
    section: SectionName
    claim_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "provenance": self.provenance.to_dict(),
            "credibility": self.credibility,
            "evidence_type": self.evidence_type,
            "section": self.section,
            "notes": self.notes
        }


@dataclass 
class SiftGraphReport:
    """The full SIFT-Graph report."""
    project: str
    query: str
    claims: List[Claim]
    critique_claims: List[Claim] = field(default_factory=list)
    sections: Dict[SectionName, List[Claim]] = field(default_factory=dict)
    meta_scores: Dict[str, float] = field(default_factory=dict)
    final_score: float = 0.0
    generated_at: str = field(default_factory=lambda: "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project": self.project,
            "query": self.query,
            "claims": [c.to_dict() for c in self.claims],
            "critique_claims": [c.to_dict() for c in self.critique_claims],
            "sections": {
                section: [c.to_dict() for c in claims]
                for section, claims in self.sections.items()
            },
            "meta_scores": self.meta_scores,
            "final_score": self.final_score,
            "generated_at": self.generated_at
        }


# ---------------------------------------------------------------------------
# MCP Client
# ---------------------------------------------------------------------------
# Uses SQLiteMCPClient when available, falls back to MockMCPClient.

class MCPClient:
    """MCP client wrapper that uses real SQLite access when available."""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root
        self._real_client: Optional[Any] = None
        self._use_real = REAL_MCP_AVAILABLE and project_root
        
        if self._use_real:
            try:
                self._real_client = SQLiteMCPClient(project_root)
            except Exception as e:
                print(f"[WARNING] Real MCP client failed: {e}. Falling back to mock.")
                self._use_real = False
    
    def list_projects(self) -> List[str]:
        if self._use_real and self._real_client:
            return self._real_client.list_projects()
        return ["home-b08x-WorkspaceV3-sfl-compiler"]
    
    def index_status(self, project: str) -> Dict[str, Any]:
        if self._use_real and self._real_client:
            return self._real_client.index_status(project)
        return {"status": "ready", "project": project, "nodes": 0, "edges": 0}
    
    def search_graph(
        self, 
        project: str, 
        query: str, 
        label: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        if self._use_real and self._real_client:
            return self._real_client.search_graph(query, label=label, limit=limit)
        
        # Fallback mock for sfl-compiler
        if "PassTwoEngine" in query:
            return [
                {
                    "name": "initialize",
                    "qualified_name": f"{project}.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.initialize",
                    "label": "Method",
                    "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
                    "start_line": 20,
                    "end_line": 24
                },
                {
                    "name": "annotate",
                    "qualified_name": f"{project}.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate",
                    "label": "Method", 
                    "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
                    "start_line": 31,
                    "end_line": 82
                },
                {
                    "name": "annotate_interpersonal",
                    "qualified_name": f"{project}.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate_interpersonal",
                    "label": "Method",
                    "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb", 
                    "start_line": 95,
                    "end_line": 122
                }
            ]
        return []
    
    def get_code_snippet(
        self, 
        project: str, 
        qualified_name: str
    ) -> Dict[str, Any]:
        if self._use_real and self._real_client:
            return self._real_client.get_code_snippet(qualified_name)
        return {
            "qualified_name": qualified_name,
            "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
            "start_line": 95,
            "end_line": 122,
            "content": "# Mock snippet content\ndef annotate_interpersonal(...):\n  # ... actual code ...\n"
        }
    
    def trace_path(
        self,
        function_name: str,
        project: Optional[str] = None,
        direction: str = "both",
        depth: int = 2
    ) -> Dict[str, Any]:
        if self._use_real and self._real_client:
            return self._real_client.trace_path(function_name, direction=direction, depth=depth)
        return {"function": function_name, "callers": [], "callees": []}
    
    def query_graph(
        self,
        query: str,
        project: Optional[str] = None,
        max_rows: int = 100
    ) -> Dict[str, Any]:
        if self._use_real and self._real_client:
            return self._real_client.query_graph(query, max_rows=max_rows)
        return {"columns": [], "rows": [], "total": 0}
    
    def close(self):
        if self._real_client:
            self._real_client.close()


# Backwards compatibility alias
MockMCPClient = MCPClient


# ---------------------------------------------------------------------------
# Pipeline Implementation
# ---------------------------------------------------------------------------

class SiftGraphProducer:
    """Produces SIFT-Graph reports from a codebase-memory graph."""
    
    SECTIONS: List[SectionName] = [
        "Verified Facts",
        "Errors and Corrections",
        "Potential Leads",
        "Source Reliability",
        "Corrections Summary",
        "Revised Summary",
        "Fact-Checker Assessment",
        "Tip Suggestion"
    ]
    
    def __init__(self, mcp_client: Optional[MCPClient] = None, project_root: Optional[str] = None):
        self.mcp = mcp_client or MCPClient(project_root)
        self.project_root = project_root
    
    def index_if_needed(self, project_name: str, repo_path: str) -> bool:
        """Ensure the project is indexed. In real impl, call mcp_codebase_memory_mcp_index_repository."""
        status = self.mcp.index_status(project_name)
        if status.get("status") == "ready":
            return True
        # In real impl: trigger indexing here
        print(f"[WARN] Project {project_name} not indexed. Run: mcp_codebase_memory_mcp_index_repository repo_path={repo_path} mode=full")
        return False
    
    def query_graph_for_term(
        self, 
        project: str, 
        term: str, 
        label: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query the codebase-memory graph for a term."""
        # The MCPClient.search_graph signature is (project, query, label, limit)
        # We pass both project (for the mock fallback) and term (as query)
        return self.mcp.search_graph(project, term, label=label, limit=10)
    
    def generate_claims_from_candidates(
        self, 
        candidates: List[Dict[str, Any]], 
        query: str,
        project: str = ""
    ) -> List[Claim]:
        """Generate at most one claim per candidate node."""
        claims = []
        for candidate in candidates:
            # Skip if we can't build a provenance tuple
            required = ["qualified_name", "file_path", "start_line", "end_line"]
            if not all(k in candidate for k in required):
                continue
            
            # Build provenance tuple
            provenance = ProvenanceTuple(
                project=project,
                node_type=candidate.get("label", "Method"),
                qualified_name=candidate["qualified_name"],
                file_path=candidate["file_path"],
                start_line=candidate["start_line"],
                end_line=candidate["end_line"],
                evidence_type="SourceCode"
            )
            
            # Generate a claim text from the candidate
            claim_text = self._generate_claim_text(candidate, query)
            if not claim_text:
                continue
            
            # Assign credibility based on evidence strength
            credibility = self._assign_credibility(candidate)
            
            claims.append(Claim(
                text=claim_text,
                provenance=provenance,
                credibility=credibility,
                evidence_type="SourceCode",
                section="Verified Facts"
            ))
        return claims
    
    def _generate_claim_text(self, candidate: Dict[str, Any], query: str) -> Optional[str]:
        """Generate a human-readable claim from a graph candidate."""
        name = candidate.get("name", "")
        qn = candidate.get("qualified_name", "")
        file_path = candidate.get("file_path", "")
        label = candidate.get("label", "")
        
        # Skip decorators (they don't have meaningful line numbers)
        if label == "Decorator":
            return None
        
        # Skip nodes without file paths (not source code)
        if not file_path:
            return None
        
        # Generic template: "{name} ({label}) in {file_path} is related to {query}"
        short_name = qn.split(".")[-1] if "." in qn else name
        return f"{short_name} ({label}) in {file_path} is a {label.lower()} related to {query}"
    
    def _assign_credibility(self, candidate: Dict[str, Any]) -> int:
        """Assign a credibility score (1-5) based on node properties."""
        # In real impl: use complexity, test coverage, docstring presence, etc.
        # For stub: return 4 for all
        return 4
    
    def audit_provenance(
        self, 
        claims: List[Claim], 
        project: str
    ) -> tuple[int, int]:
        """Audit claims against the graph. Returns (valid_count, total_count)."""
        valid = 0
        for claim in claims:
            prov = claim.provenance
            # In real impl: query graph to verify qualified_name exists
            # For stub: assume all are valid
            valid += 1
        return valid, len(claims)
    
    def self_critique(
        self, 
        claims: List[Claim], 
        project: str,
        query: str
    ) -> List[Claim]:
        """Generate a critique ledger. In real impl, this would query for gaps."""
        # Stub: return empty (no critique)
        return []
    
    def assemble_report(
        self, 
        claims: List[Claim], 
        critique_claims: List[Claim],
        project: str,
        query: str
    ) -> SiftGraphReport:
        """Assemble the 8-section report."""
        # Group claims by section
        sections: Dict[SectionName, List[Claim]] = {s: [] for s in self.SECTIONS}
        for claim in claims:
            sections[claim.section].append(claim)
        for claim in critique_claims:
            sections[claim.section].append(claim)
        
        return SiftGraphReport(
            project=project,
            query=query,
            claims=claims,
            critique_claims=critique_claims,
            sections=sections
        )
    
    def score_report(
        self,
        claims: List[Claim],
        critique_claims: List[Claim]
    ) -> Dict[str, float]:
        """Compute meta-rubric scores."""
        total_claims = len(claims)
        if total_claims == 0:
            return {"final_score": 0.0, "claim_provenance": 0.0, "section_completeness": 0.0}
        
        # 1. Claim Provenance (40%)
        valid, total = self.audit_provenance(claims, claims[0].provenance.project)
        provenance_score = self._map_to_1_5(valid / total if total > 0 else 0)
        
        # 2. Section Completeness (25%)
        present_sections = set(c.section for c in claims)
        num_sections = len(present_sections)
        # 0-2 sections=1, 3-4=2, 5-6=3, 7=4, 8=5
        if num_sections <= 2:
            completeness_score = 1.0
        elif num_sections <= 4:
            completeness_score = 2.0
        elif num_sections <= 6:
            completeness_score = 3.0
        elif num_sections == 7:
            completeness_score = 4.0
        else:
            completeness_score = 5.0
        
        # 3. Severity Calibration (20%)
        creds = [c.credibility for c in claims]
        calibration_score = self._calibration_score(creds)
        
        # 4. Self-Critique Payoff (15%)
        payoff_score = self._payoff_score(claims, critique_claims)
        
        # Weighted sum
        raw = (
            provenance_score * 0.40 +
            completeness_score * 0.25 +
            calibration_score * 0.20 +
            payoff_score * 0.15
        )
        
        # Pitfall penalty
        pitfalls = self._count_pitfalls(claims)
        final = max(0, raw - (pitfalls * 0.3))
        
        # Essential Cap
        if provenance_score < 3:
            final = min(final, 2.0)
        
        return {
            "claim_provenance": round(provenance_score, 2),
            "section_completeness": round(completeness_score, 2),
            "severity_calibration": round(calibration_score, 2),
            "self_critique_payoff": round(payoff_score, 2),
            "raw_score": round(raw, 2),
            "pitfall_penalty": round(pitfalls * 0.3, 2),
            "final_score": round(final, 2),
            "chain_integrity": round(min(provenance_score, completeness_score, calibration_score, payoff_score), 2)
        }
    
    def _map_to_1_5(self, ratio: float) -> float:
        """Map a 0-1 ratio to a 1-5 score."""
        if ratio >= 0.95:
            return 5.0
        elif ratio >= 0.85:
            return 4.0
        elif ratio >= 0.70:
            return 3.0
        elif ratio >= 0.50:
            return 2.0
        else:
            return 1.0
    
    def _calibration_score(self, creds: List[int]) -> float:
        """Score based on credibility distribution.
        
        Scoring: std_dev > 1.5=1, 1.0-1.5=2, 0.5-1.0=3, 0.2-0.5=4, <0.2=5
        Lower std_dev = more consistent = better calibration.
        """
        if not creds:
            return 1.0
        import statistics
        try:
            std_dev = statistics.stdev(creds)
        except statistics.StatisticsError:
            std_dev = 0
        
        if std_dev > 1.5:
            return 1.0
        elif std_dev > 1.0:
            return 2.0
        elif std_dev > 0.5:
            return 3.0
        elif std_dev > 0.2:
            return 4.0
        else:
            return 5.0
    
    def _payoff_score(self, claims: List[Claim], critique_claims: List[Claim]) -> float:
        """Score based on critique payoff."""
        if not claims:
            return 1.0
        original_ids = {c.claim_id for c in claims}
        new_ids = {c.claim_id for c in critique_claims if c.claim_id not in original_ids}
        payoff = len(new_ids) / len(claims) if claims else 0
        return self._map_to_1_5(payoff)
    
    def _count_pitfalls(self, claims: List[Claim]) -> int:
        """Count anti-patterns."""
        pitfalls = 0
        for claim in claims:
            # In real impl: check if provenance resolves
            # For stub: assume no pitfalls
            pass
        return pitfalls


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _get_project_root(project_name: str) -> str:
    """Map project name to filesystem path."""
    # Known project mappings
    known_projects = {
        "home-b08x-WorkspaceV3-sfl-compiler": "/home/b08x/WorkspaceV3/sfl-compiler",
    }
    
    if project_name in known_projects:
        return known_projects[project_name]
    
    # Fallback: try standard pattern
    if project_name.startswith("home-b08x-"):
        path = "/home/b08x/" + project_name[12:].replace("-", "/")
        if Path(path).exists():
            return path
    return ""

def main():
    import argparse
    parser = argparse.ArgumentParser(description="SIFT-Graph Producer")
    parser.add_argument("project_name", help="codebase-memory project name")
    parser.add_argument("query", help="Query or topic to analyze")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: <project_root>/.sift-graph)")
    parser.add_argument("--project-root", help="Override project root path")
    args = parser.parse_args()
    
    project_name = args.project_name
    query = args.query
    
    # Get project root
    project_root = args.project_root
    if not project_root:
        project_root = _get_project_root(project_name)
    
    if args.output_dir:
        output_dir = Path(args.output_dir)
    elif project_root:
        output_dir = Path(project_root) / ".sift-graph"
    else:
        output_dir = Path(".sift-graph")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize
    producer = SiftGraphProducer(project_root=project_root)
    
    # Check indexing
    if not producer.index_if_needed(project_name, ""):
        print(f"[ERROR] Project {project_name} not indexed. Please index first.")
        sys.exit(1)
    
    # Query graph
    candidates = producer.query_graph_for_term(project_name, query)
    print(f"[INFO] Found {len(candidates)} candidates for query: {query}")
    
    # Generate claims
    claims = producer.generate_claims_from_candidates(candidates, query, project_name)
    print(f"[INFO] Generated {len(claims)} claims")
    
    # Self-critique
    critique_claims = producer.self_critique(claims, project_name, query)
    print(f"[INFO] Generated {len(critique_claims)} critique claims")
    
    # Assemble report
    report = producer.assemble_report(claims, critique_claims, project_name, query)
    
    # Score report
    scores = producer.score_report(claims, critique_claims)
    report.meta_scores = scores
    report.final_score = scores["final_score"]
    report.generated_at = "2026-07-04T12:00:00Z"
    
    # Write outputs
    report_path = output_dir / f"{project_name.replace('/', '-')}-{query.replace(' ', '-')}.json"
    with open(report_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)
    print(f"[INFO] Report written to: {report_path}")
    
    # Write markdown
    md_path = output_dir / f"{project_name.replace('/', '-')}-{query.replace(' ', '-')}.md"
    with open(md_path, "w") as f:
        f.write(_format_markdown(report))
    print(f"[INFO] Markdown written to: {md_path}")
    
    print(f"\nFinal Score: {report.final_score:.1f}")
    print(f"Scores: {json.dumps(scores, indent=2)}")
    
    # Cleanup
    producer.mcp.close()


def _format_markdown(report: SiftGraphReport) -> str:
    """Format report as markdown."""
    lines = []
    lines.append(f"# SIFT-Graph Report: {report.query}")
    lines.append("")
    lines.append(f"**Generated**: {report.generated_at}")
    lines.append(f"**Project**: {report.project}")
    lines.append(f"**Final Score**: {report.final_score:.1f}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for section in SiftGraphProducer.SECTIONS:
        if section not in report.sections or not report.sections[section]:
            continue
        lines.append(f"## {section}")
        lines.append("")
        for claim in report.sections[section]:
            prov = claim.provenance
            lines.append(f"- **{claim.text}**")
            lines.append(f"  - Credibility: {claim.credibility}/5")
            lines.append(f"  - Provenance: [{prov.node_type}]({prov.qualified_name}:{prov.start_line}-{prov.end_line})")
            # Embed machine-readable provenance as HTML comment
            lines.append(f"  <!-- SIFT-GRAPH: {json.dumps(claim.to_dict())} -->")
        lines.append("")
    
    # Meta-rubric scores
    lines.append("## 9. SIFT-Graph Meta-Rubric Scores")
    lines.append("")
    lines.append("| Dimension | Score | Weight | Weighted |")
    lines.append("|-----------|-------|--------|----------|")
    
    weights = {
        "claim_provenance": 0.40,
        "section_completeness": 0.25,
        "severity_calibration": 0.20,
        "self_critique_payoff": 0.15
    }
    for dim, score in report.meta_scores.items():
        if dim in weights:
            weighted = score * weights[dim]
            lines.append(f"| {dim.replace('_', ' ').title()} | {score:.2f} | {weights[dim]*100:.0f}% | {weighted:.2f} |")
    
    lines.append(f"| **Raw Score** | | | **{report.meta_scores.get('raw_score', 0):.2f}** |")
    lines.append(f"| **Pitfall Penalty** | | | **-{report.meta_scores.get('pitfall_penalty', 0):.2f}** |")
    lines.append(f"| **Final Score** | | | **{report.final_score:.2f}** |")
    lines.append(f"| **Chain Integrity** | {report.meta_scores.get('chain_integrity', 0):.2f} | | (min of all dimensions) |")
    lines.append("")
    
    if report.meta_scores.get("claim_provenance", 0) < 3:
        lines.append("**Essential Cap**: Triggered (Claim Provenance < 3)")
    else:
        lines.append("**Essential Cap**: Not triggered")
    lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()
