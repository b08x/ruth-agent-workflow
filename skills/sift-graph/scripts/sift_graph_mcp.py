#!/usr/bin/env python3
"""
SIFT-Graph Real MCP Client

Replaces MockMCPClient with direct SQLite access to the codebase-memory graph database.
The graph is stored at <project_root>/.codebase-memory/graph.db.zst (Zstandard compressed).

Usage:
    from sift_graph_mcp import SQLiteMCPClient
    
    client = SQLiteMCPClient("/home/b08x/WorkspaceV3/sfl-compiler")
    results = client.search_graph("PassTwoEngine", label="Method")

Author: b08x (with Hermes)
Date: 2026-07-04
"""

import json
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class SQLiteMCPClient:
    """Real MCP client using direct SQLite access to the codebase-memory graph."""
    
    def __init__(self, project_root: str):
        """
        Initialize the client for a specific project.
        
        Args:
            project_root: Absolute path to the project root (e.g., /home/b08x/WorkspaceV3/sfl-compiler)
        """
        self.project_root = Path(project_root)
        self.graph_path = self.project_root / ".codebase-memory" / "graph.db.zst"
        self.artifact_path = self.project_root / ".codebase-memory" / "artifact.json"
        self._db_path: Optional[Path] = None
        self._conn: Optional[sqlite3.Connection] = None
        self._project_name: Optional[str] = None
        
        if not self.graph_path.exists():
            raise FileNotFoundError(
                f"Graph database not found at {self.graph_path}. "
                f"Run: mcp_codebase_memory_mcp_index_repository repo_path={project_root} mode=full"
            )
    
    def _decompress_graph(self) -> Path:
        """Decompress the graph.db.zst file to a temporary location."""
        if self._db_path and self._db_path.exists():
            return self._db_path
        
        # Create a persistent temp file (don't use /tmp directly)
        temp_dir = Path(tempfile.gettempdir()) / "sift_graph_mcp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        db_path = temp_dir / f"{self.project_root.name}.db"
        
        # Decompress using zstd
        result = subprocess.run(
            ["zstd", "-d", str(self.graph_path), "-o", str(db_path), "-f"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to decompress graph: {result.stderr}")
        
        self._db_path = db_path
        return db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a SQLite connection to the decompressed graph database."""
        if self._conn is None:
            db_path = self._decompress_graph()
            self._conn = sqlite3.connect(str(db_path))
            self._conn.row_factory = sqlite3.Row
        
        # Load project name from artifact
        if self._project_name is None and self.artifact_path.exists():
            with open(self.artifact_path) as f:
                artifact = json.load(f)
                self._project_name = artifact.get("project")
        
        return self._conn
    
    def list_projects(self) -> List[str]:
        """List all indexed projects (from the projects table)."""
        conn = self._get_connection()
        cursor = conn.execute("SELECT name FROM projects")
        return [row["name"] for row in cursor.fetchall()]
    
    def index_status(self, project_name: str) -> Dict[str, Any]:
        """Get the indexing status of a project."""
        artifact_path = self.project_root / ".codebase-memory" / "artifact.json"
        if not artifact_path.exists():
            return {"status": "not_found", "project": project_name}
        
        with open(artifact_path) as f:
            artifact = json.load(f)
        
        return {
            "status": "ready" if artifact.get("nodes", 0) > 0 else "empty",
            "project": artifact.get("project", project_name),
            "nodes": artifact.get("nodes", 0),
            "edges": artifact.get("edges", 0),
            "indexed_at": artifact.get("indexed_at")
        }
    
    def search_graph(
        self,
        query: str,
        project: Optional[str] = None,
        label: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search the graph using BM25 full-text search.
        
        Args:
            query: Search query (e.g., "PassTwoEngine")
            project: Project name (defaults to current project)
            label: Filter by node label (e.g., "Method", "Class")
            limit: Maximum number of results
        
        Returns:
            List of node dictionaries with qualified_name, file_path, start_line, end_line, etc.
        """
        conn = self._get_connection()
        project = project or self._project_name
        
        # Build the FTS5 query
        # Escape special characters and use prefix matching
        fts_query = " ".join(f'"{word}"*' for word in query.split() if word)
        
        if not fts_query:
            return []
        
        # Query with optional label filter
        if label:
            sql = """
                SELECT n.name, n.qualified_name, n.label, n.file_path,
                       n.start_line, n.end_line, n.properties
                FROM nodes n
                JOIN nodes_fts fts ON n.id = fts.rowid
                WHERE nodes_fts MATCH ?
                  AND n.label = ?
                ORDER BY rank
                LIMIT ?
            """
            cursor = conn.execute(sql, (fts_query, label, limit))
        else:
            sql = """
                SELECT n.name, n.qualified_name, n.label, n.file_path,
                       n.start_line, n.end_line, n.properties
                FROM nodes n
                JOIN nodes_fts fts ON n.id = fts.rowid
                WHERE nodes_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """
            cursor = conn.execute(sql, (fts_query, limit))
        
        results = []
        for row in cursor.fetchall():
            # Parse properties JSON
            try:
                props = json.loads(row["properties"]) if row["properties"] else {}
            except json.JSONDecodeError:
                props = {}
            
            results.append({
                "name": row["name"],
                "qualified_name": row["qualified_name"],
                "label": row["label"],
                "file_path": row["file_path"],
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "complexity": props.get("complexity", 0),
                "properties": props
            })
        
        return results
    
    def get_code_snippet(
        self,
        qualified_name: str,
        project: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the actual code snippet for a node.
        
        Args:
            qualified_name: Full qualified name of the node
            project: Project name (defaults to current project)
        
        Returns:
            Dictionary with file_path, start_line, end_line, and content
        """
        conn = self._get_connection()
        
        # Get node info
        cursor = conn.execute(
            "SELECT file_path, start_line, end_line, name, label FROM nodes WHERE qualified_name = ?",
            (qualified_name,)
        )
        row = cursor.fetchone()
        
        if not row:
            return {"error": f"Node not found: {qualified_name}"}
        
        # Read the actual file content
        file_path = self.project_root / row["file_path"]
        if not file_path.exists():
            return {
                "qualified_name": qualified_name,
                "file_path": row["file_path"],
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "content": "[File not found]"
            }
        
        with open(file_path) as f:
            lines = f.readlines()
        
        start = max(0, row["start_line"] - 1)
        end = min(len(lines), row["end_line"])
        content = "".join(lines[start:end])
        
        return {
            "qualified_name": qualified_name,
            "name": row["name"],
            "label": row["label"],
            "file_path": row["file_path"],
            "start_line": row["start_line"],
            "end_line": row["end_line"],
            "content": content
        }
    
    def trace_path(
        self,
        function_name: str,
        project: Optional[str] = None,
        direction: str = "both",
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        Trace call paths from a function.
        
        Args:
            function_name: Name or qualified_name of the function
            project: Project name (defaults to current project)
            direction: "inbound", "outbound", or "both"
            depth: Maximum depth to trace
        
        Returns:
            Dictionary with callers, callees, and paths
        """
        conn = self._get_connection()
        
        # Find the function node
        cursor = conn.execute(
            "SELECT id, qualified_name, name, label FROM nodes WHERE qualified_name LIKE ? OR name = ? LIMIT 1",
            (f"%{function_name}%", function_name)
        )
        func_row = cursor.fetchone()
        
        if not func_row:
            return {"error": f"Function not found: {function_name}", "callers": [], "callees": []}
        
        func_id = func_row["id"]
        result = {
            "function": func_row["qualified_name"],
            "callers": [],
            "callees": []
        }
        
        # Outbound (callees)
        if direction in ("outbound", "both"):
            cursor = conn.execute("""
                SELECT n.name, n.qualified_name, n.label, n.file_path, n.start_line, n.end_line,
                       e.edge_type
                FROM edges e
                JOIN nodes n ON e.target_id = n.id
                WHERE e.source_id = ?
                LIMIT 50
            """, (func_id,))
            
            for row in cursor.fetchall():
                result["callees"].append({
                    "name": row["name"],
                    "qualified_name": row["qualified_name"],
                    "label": row["label"],
                    "file_path": row["file_path"],
                    "start_line": row["start_line"],
                    "end_line": row["end_line"],
                    "edge_type": row["edge_type"]
                })
        
        # Inbound (callers)
        if direction in ("inbound", "both"):
            cursor = conn.execute("""
                SELECT n.name, n.qualified_name, n.label, n.file_path, n.start_line, n.end_line,
                       e.edge_type
                FROM edges e
                JOIN nodes n ON e.source_id = n.id
                WHERE e.target_id = ?
                LIMIT 50
            """, (func_id,))
            
            for row in cursor.fetchall():
                result["callers"].append({
                    "name": row["name"],
                    "qualified_name": row["qualified_name"],
                    "label": row["label"],
                    "file_path": row["file_path"],
                    "start_line": row["start_line"],
                    "end_line": row["end_line"],
                    "edge_type": row["edge_type"]
                })
        
        return result
    
    def query_graph(
        self,
        query: str,
        project: Optional[str] = None,
        max_rows: int = 100
    ) -> Dict[str, Any]:
        """
        Execute a raw SQL query against the graph.
        
        Args:
            query: SQL query (use with caution)
            project: Project name (defaults to current project)
            max_rows: Maximum rows to return
        
        Returns:
            Dictionary with columns, rows, and total count
        """
        conn = self._get_connection()
        cursor = conn.execute(query)
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchmany(max_rows)
        
        return {
            "columns": columns,
            "rows": [dict(zip(columns, row)) for row in rows],
            "total": len(rows)
        }
    
    def get_graph_schema(self) -> Dict[str, Any]:
        """Get the schema of the graph database."""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {"tables": []}
        for table in tables:
            cursor = conn.execute(f"PRAGMA table_info({table})")
            columns = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]
            schema["tables"].append({"name": table, "columns": columns})
        
        return schema
    
    def close(self):
        """Close the database connection and clean up temp files."""
        if self._conn:
            self._conn.close()
            self._conn = None
        
        if self._db_path and self._db_path.exists():
            self._db_path.unlink()
            self._db_path = None


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python sift_graph_mcp.py <project_root> <query>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    query = sys.argv[2]
    
    client = SQLiteMCPClient(project_root)
    
    print(f"Project: {project_root}")
    print(f"Status: {client.index_status('')}")
    print(f"\nSearching for: {query}")
    
    results = client.search_graph(query, label="Method", limit=5)
    print(f"\nFound {len(results)} results:")
    for r in results:
        print(f"  - {r['qualified_name']} ({r['file_path']}:{r['start_line']}-{r['end_line']})")
    
    if results:
        print(f"\nCode snippet for first result:")
        snippet = client.get_code_snippet(results[0]["qualified_name"])
        print(f"  File: {snippet['file_path']}:{snippet['start_line']}-{snippet['end_line']}")
        print(f"  Content preview: {snippet['content'][:200]}...")
    
    client.close()
