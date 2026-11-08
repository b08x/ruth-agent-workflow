# SIFT-Graph Provenance Tuple Examples

This file contains example provenance tuples for different types of claims.
These are the tuples that MUST accompany every claim in a SIFT-Graph report.

## Format

Every provenance tuple is a JSON object with these fields:

```json
{
  "project": "string",           // codebase-memory project name
  "node_type": "string",        // Function | Method | Class | Variable | File | Module | Section | Folder | Route | Edge
  "qualified_name": "string",   // Full qualified name from the graph
  "file_path": "string",        // Absolute or project-relative file path
  "start_line": integer,         // 1-indexed start line
  "end_line": integer,          // 1-indexed end line
  "evidence_type": "string",    // SourceCode | Documentation | Test | Config | Comment | ExternalSource | Inference
  "snippet": "string",          // Optional: actual text from start_line to end_line
  "edge_type": "string",        // Optional: for edge provenance (CALLS, IMPORTS, etc.)
  "edge_source": "string",      // Optional: for edge provenance, source node qualified_name
  "edge_target": "string"       // Optional: for edge provenance, target node qualified_name
}
```

---

## Example 1: Method Provenance (Ruby)

**Claim**: "PassTwoEngine#annotate_interpersonal uses a circuit breaker with 3 retries."

**Provenance Tuple**:
```json
{
  "project": "home-b08x-WorkspaceV3-sfl-compiler",
  "node_type": "Method",
  "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate_interpersonal",
  "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
  "start_line": 95,
  "end_line": 122,
  "evidence_type": "SourceCode",
  "snippet": "def annotate_interpersonal(clause, syntactic, ideational)\n  circuit_breaker = Crab::CircuitBreaker.new(max_retries: 3)\n  circuit_breaker.call do\n    # ... annotation logic ...\n  end\nend"
}
```

**Verification Query**:
```cypher
MATCH (m:Method {qualified_name: "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate_interpersonal"})
RETURN m.file_path, m.start_line, m.end_line
```

---

## Example 2: Function Provenance (Python)

**Claim**: "The SflGebCompilerCrew uses a sequential strategy with 5 agents."

**Provenance Tuple**:
```json
{
  "project": "home-b08x-WorkspaceV3-crews-sfl_geb_compiler_v1_crewai-project",
  "node_type": "Function",
  "qualified_name": "home-b08x-WorkspaceV3-crews-sfl_geb_compiler_v1_crewai-project.src.sfl_geb_compiler.crew.crew",
  "file_path": "src/sfl_geb_compiler/crew.py",
  "start_line": 1,
  "end_line": 50,
  "evidence_type": "SourceCode",
  "snippet": "def crew() -> CrewAI.Crew:\n    return CrewAI.Crew(\n        agents=[...],\n        tasks=[...],\n        process=Sequential()\n    )"
}
```

---

## Example 3: Call Edge Provenance

**Claim**: "PassTwoEngine#annotate calls DerivationHash.compute."

**Provenance Tuple**:
```json
{
  "project": "home-b08x-WorkspaceV3-sfl-compiler",
  "node_type": "Edge",
  "edge_type": "CALLS",
  "edge_source": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate",
  "edge_target": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.types.DerivationHash.compute",
  "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
  "start_line": 31,
  "end_line": 82,
  "evidence_type": "SourceCode"
}
```

**Verification Query**:
```cypher
MATCH (a)-[r:CALLS]->(b)
WHERE a.qualified_name = "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate"
  AND b.qualified_name = "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.types.DerivationHash.compute"
RETURN r
```

---

## Example 4: File-Level Provenance

**Claim**: "The pass_two_engine.rb file contains the PassTwoEngine class."

**Provenance Tuple**:
```json
{
  "project": "home-b08x-WorkspaceV3-sfl-compiler",
  "node_type": "File",
  "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.rb",
  "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
  "start_line": 1,
  "end_line": 600,
  "evidence_type": "SourceCode"
}
```

---

## Example 5: External Source Provenance

**Claim**: "The Harvard Health article states that music reduces stress hormones."

**Provenance Tuple**:
```json
{
  "project": "N/A",
  "node_type": "ExternalSource",
  "qualified_name": "https://www.health.harvard.edu/staying-healthy/music-and-health",
  "file_path": "https://www.health.harvard.edu/staying-healthy/music-and-health",
  "start_line": 0,
  "end_line": 0,
  "evidence_type": "ExternalSource",
  "snippet": "Music can influence brain states by affecting neural pathways and reducing stress hormones."
}
```

**Note**: ExternalSource provenance cannot be verified against the codebase-memory graph. These claims should be flagged for manual review and do not contribute to the Claim Provenance score.

---

## Example 6: Documentation Provenance

**Claim**: "The README states that SFL-GEB v1 uses a 5-agent sequential pipeline."

**Provenance Tuple**:
```json
{
  "project": "home-b08x-WorkspaceV3-crews-sfl_geb_compiler_v1_crewai-project",
  "node_type": "File",
  "qualified_name": "home-b08x-WorkspaceV3-crews-sfl_geb_compiler_v1_crewai-project.README.md",
  "file_path": "README.md",
  "start_line": 1,
  "end_line": 50,
  "evidence_type": "Documentation",
  "snippet": "# SFL-GEB Compiler v1\n\nA 5-agent sequential CrewAI pipeline..."
}
```

---

## Audit Pass Example

Given a SIFT-Graph report with claims, the audit pass verifies each provenance tuple:

```python
from sift_graph import SiftGraphProducer, Claim, ProvenanceTuple

# Load report
report = ...  # from JSON

# Initialize producer with real MCP client
producer = SiftGraphProducer(mcp_client=RealMCPClient())

# Audit each claim
valid_count = 0
for claim in report.claims:
    prov = claim.provenance
    
    # Query the graph to verify the tuple
    if prov.node_type == "Method":
        result = producer.mcp.search_graph(
            project=prov.project,
            query=prov.qualified_name,
            label="Method"
        )
        if result:
            valid_count += 1
    
    elif prov.node_type == "Edge":
        result = producer.mcp.query_graph(
            project=prov.project,
            query=f"""
                MATCH (a)-[r:{prov.edge_type}]->(b)
                WHERE a.qualified_name = $source AND b.qualified_name = $target
                RETURN r
            """,
            params={"source": prov.edge_source, "target": prov.edge_target}
        )
        if result["total"] > 0:
            valid_count += 1

provenance_coverage = valid_count / len(report.claims)
```

---

## Invalid Provenance Examples

These tuples would FAIL the audit pass:

### Invalid 1: Non-existent qualified_name
```json
{
  "project": "home-b08x-WorkspaceV3-sfl-compiler",
  "node_type": "Method",
  "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.nonexistent_method",
  "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
  "start_line": 1,
  "end_line": 10,
  "evidence_type": "SourceCode"
}
```
**Reason**: No such method exists in the graph.

### Invalid 2: Wrong line range
```json
{
  "project": "home-b08x-WorkspaceV3-sfl-compiler",
  "node_type": "Method",
  "qualified_name": "home-b08x-WorkspaceV3-sfl-compiler.lib.sfl.compiler.pass_two.pass_two_engine.SFL.Compiler.PassTwoEngine.annotate",
  "file_path": "lib/sfl/compiler/pass_two/pass_two_engine.rb",
  "start_line": 1000,  // Method actually starts at line 31
  "end_line": 2000,
  "evidence_type": "SourceCode"
}
```
**Reason**: Line range does not match the graph's recorded range.

### Invalid 3: Missing required field
```json
{
  "project": "home-b08x-WorkspaceV3-sfl-compiler",
  "node_type": "Method",
  "qualified_name": "...",
  // Missing file_path, start_line, end_line
  "evidence_type": "SourceCode"
}
```
**Reason**: Required fields are missing.
