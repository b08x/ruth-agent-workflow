#!/usr/bin/env python3
"""
SIFT-Graph CrewAI Implementation

A CrewAI-based implementation of the SIFT-Graph protocol.
Uses the codebase-memory MCP tool for graph queries.

Usage:
    python sift_graph_crewai.py <project_name> <query>

Example:
    python sift_graph_crewai.py home-b08x-WorkspaceV3-crews-sfl_geb_compiler_v1_crewai-project "crew"

Author: b08x (with Hermes)
Date: 2026-07-04
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Check if CrewAI is available
try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("[WARNING] CrewAI not installed. Falling back to functional pipeline.")

# Check if MCP tools are available
try:
    from hermes_tools import mcp_codebase_memory_mcp_search_graph
    MCP_TOOLS_AVAILABLE = True
except ImportError:
    MCP_TOOLS_AVAILABLE = False
    print("[WARNING] Hermes MCP tools not available. Falling back to SQLite client.")

# Fallback to our SQLite client
if not MCP_TOOLS_AVAILABLE:
    sys.path.insert(0, str(Path(__file__).parent))
    from sift_graph_mcp import SQLiteMCPClient


class SiftGraphCrew:
    """CrewAI implementation of SIFT-Graph."""
    
    def __init__(self, project_name: str, project_root: str):
        self.project_name = project_name
        self.project_root = project_root
        self._crew: Optional[Crew] = None
        self._graph_client = None
        
        if MCP_TOOLS_AVAILABLE:
            # Use Hermes MCP tools directly
            self._use_mcp_tools = True
        else:
            # Use SQLite client
            self._use_mcp_tools = False
            self._graph_client = SQLiteMCPClient(project_root)
    
    def _get_graph_client(self):
        """Get the graph client (MCP tools or SQLite)."""
        if self._use_mcp_tools:
            return None  # MCP tools are called directly
        return self._graph_client
    
    def search_graph(self, query: str, label: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the codebase-memory graph."""
        if self._use_mcp_tools:
            # Call Hermes MCP tool directly
            results = mcp_codebase_memory_mcp_search_graph(
                project=self.project_name,
                query=query,
                label=label,
                limit=limit
            )
            return results.get("results", [])
        else:
            return self._graph_client.search_graph(query, label=label, limit=limit)
    
    def get_code_snippet(self, qualified_name: str) -> Dict[str, Any]:
        """Get code snippet for a node."""
        if self._use_mcp_tools:
            # Call Hermes MCP tool directly
            result = mcp_codebase_memory_mcp_get_code_snippet(
                qualified_name=qualified_name,
                project=self.project_name
            )
            return result
        else:
            return self._graph_client.get_code_snippet(qualified_name)
    
    def create_crew(self) -> Crew:
        """Create the SIFT-Graph CrewAI crew."""
        if not CREWAI_AVAILABLE:
            raise ImportError("CrewAI not installed")
        
        # Define agents
        graph_analyst = Agent(
            role="Codebase Graph Analyst",
            goal="Query the codebase-memory knowledge graph to find relevant nodes and edges",
            backstory="""
                You are an expert at querying codebase knowledge graphs.
                You use the codebase-memory MCP tool to find functions, classes, methods,
                and their relationships (CALLS, IMPORTS, etc.).
                You return structured data, not prose.
            """,
            verbose=True,
            allow_delegation=False
        )
        
        claim_generator = Agent(
            role="Claim Generator",
            goal="Generate factual claims from graph nodes with provenance tuples",
            backstory="""
                You take graph nodes (functions, classes, methods) and generate
                human-readable claims with machine-readable provenance tuples.
                Every claim MUST include a provenance tuple that can be verified
                against the codebase-memory graph.
            """,
            verbose=True,
            allow_delegation=False
        )
        
        provenance_auditor = Agent(
            role="Provenance Auditor",
            goal="Verify that every claim's provenance tuple resolves to the graph",
            backstory="""
                You audit claims by checking that their provenance tuples resolve
                to actual nodes/edges in the codebase-memory graph.
                You flag any claims with invalid provenance.
            """,
            verbose=True,
            allow_delegation=False
        )
        
        report_assembler = Agent(
            role="Report Assembler",
            goal="Assemble claims into an 8-section SIFT report with meta-rubric scores",
            backstory="""
                You take audited claims and assemble them into a structured
                SIFT report with 8 sections. You also compute the meta-rubric
                scores (Claim Provenance, Section Completeness, Severity Calibration,
                Self-Critique Payoff) and apply the Essential Cap.
            """,
            verbose=True,
            allow_delegation=False
        )
        
        # Define tasks
        query_task = Task(
            description=f"""
                Query the codebase-memory graph for the term '{self.query}'.
                Use search_graph with label=Function, Class, Method, File.
                Return a list of candidate nodes with qualified_name, file_path, start_line, end_line.
            """,
            agent=graph_analyst,
            expected_output="List of candidate nodes as JSON"
        )
        
        claim_task = Task(
            description="""
                For each candidate node, generate a claim with:
                - text: human-readable claim
                - provenance: tuple with project, node_type, qualified_name, file_path, start_line, end_line, evidence_type
                - credibility: 1-5 score
                - evidence_type: SourceCode, Documentation, Test, Config, Comment, ExternalSource, or Inference
                - section: one of the 8 SIFT sections
            """,
            agent=claim_generator,
            expected_output="List of claims as JSON"
        )
        
        audit_task = Task(
            description="""
                For each claim, verify that the provenance tuple resolves to the graph.
                Use search_graph or get_code_snippet to check.
                Return: valid_count, total_count, list of invalid claims
            """,
            agent=provenance_auditor,
            expected_output="Audit results as JSON"
        )
        
        assemble_task = Task(
            description="""
                Assemble valid claims into an 8-section SIFT report.
                Compute meta-rubric scores:
                - Claim Provenance: valid_count / total_count (mapped to 1-5)
                - Section Completeness: number of sections with claims (1-5)
                - Severity Calibration: std_dev of credibility scores (1-5)
                - Self-Critique Payoff: fraction of critique claims that were new
                Apply Essential Cap: if Claim Provenance < 3, cap final score at 2.0
                Apply Pitfall Penalty: -0.3 per anti-pattern
            """,
            agent=report_assembler,
            expected_output="Complete SIFT-Graph report as JSON"
        )
        
        # Create crew with sequential process
        self._crew = Crew(
            agents=[graph_analyst, claim_generator, provenance_auditor, report_assembler],
            tasks=[query_task, claim_task, audit_task, assemble_task],
            process=Process.sequential,
            verbose=2
        )
        
        return self._crew
    
    def run(self, query: str) -> Dict[str, Any]:
        """Run the SIFT-Graph crew on a query."""
        self.query = query
        
        if CREWAI_AVAILABLE:
            crew = self.create_crew()
            result = crew.kickoff()
            return result
        else:
            # Fallback to functional pipeline
            print("[INFO] Using functional pipeline (CrewAI not available)")
            return self._run_functional(query)
    
    def _run_functional(self, query: str) -> Dict[str, Any]:
        """Fallback to functional pipeline."""
        # This is a simplified version of the functional pipeline
        # In practice, you'd import and use SiftGraphProducer
        from sift_graph import SiftGraphProducer
        
        producer = SiftGraphProducer(project_root=self.project_root)
        
        # Query graph
        candidates = producer.query_graph_for_term(self.project_name, query)
        print(f"[INFO] Found {len(candidates)} candidates")
        
        # Generate claims
        claims = producer.generate_claims_from_candidates(candidates, query, self.project_name)
        print(f"[INFO] Generated {len(claims)} claims")
        
        # Self-critique
        critique_claims = producer.self_critique(claims, query)
        print(f"[INFO] Generated {len(critique_claims)} critique claims")
        
        # Assemble report
        report = producer.assemble_report(
            project=self.project_name,
            query=query,
            claims=claims,
            critique_claims=critique_claims
        )
        
        # Score report
        scores = producer.score_report(claims, critique_claims)
        report.meta_scores = scores
        report.final_score = scores["final_score"]
        
        producer.mcp.close()
        
        return report.to_dict()
    
    def close(self):
        """Clean up resources."""
        if self._graph_client:
            self._graph_client.close()


def _get_project_root(project_name: str) -> str:
    """Map project name to filesystem path."""
    known_projects = {
        "home-b08x-WorkspaceV3-sfl-compiler": "/home/b08x/WorkspaceV3/sfl-compiler",
        "home-b08x-WorkspaceV3-crews-sfl_geb_compiler_v1_crewai-project": "/home/b08x/WorkspaceV3/crews/sfl_geb_compiler_v1_crewai-project",
    }
    
    if project_name in known_projects:
        return known_projects[project_name]
    
    if project_name.startswith("home-b08x-"):
        path = "/home/b08x/" + project_name[12:].replace("-", "/")
        if Path(path).exists():
            return path
    return ""


def main():
    if len(sys.argv) < 3:
        print("Usage: python sift_graph_crewai.py <project_name> <query>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    query = sys.argv[2]
    
    project_root = _get_project_root(project_name)
    if not project_root:
        print(f"[ERROR] Cannot resolve project root for {project_name}")
        sys.exit(1)
    
    print(f"[INFO] Running SIFT-Graph on {project_name}")
    print(f"[INFO] Project root: {project_root}")
    
    crew = SiftGraphCrew(project_name, project_root)
    result = crew.run(query)
    
    # Print result
    print("\n" + "="*60)
    print("SIFT-Graph Report")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    crew.close()


if __name__ == "__main__":
    main()
