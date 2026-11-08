# QMD MCP Server Setup

## Install

```bash
git clone https://github.com/b08x/qmd.git
cd qmd
npm install
npm link
qmd collection add ~/path/to/markdown --name myknowledge
qmd embed
```

Installed from the source repository at https://github.com/b08x/qmd.git (`npm link` puts the `qmd` binary on PATH).

## Configure MCP Client

**Claude Code** (`~/.claude/settings.json`):
```json
{
  "mcpServers": {
    "qmd": { "command": "qmd", "args": ["mcp"] }
  }
}
```

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "qmd": { "command": "qmd", "args": ["mcp"] }
  }
}
```

**Mistral Vibe** (`~/.vibe/config.toml`):
```toml
[[mcp_servers]]
name = "qmd"
transport = "stdio"
command = "qmd"
args = ["mcp"]
```

**OpenClaw** (`~/.openclaw/openclaw.json`):
```json
{
  "mcp": {
    "servers": {
      "qmd": { "command": "qmd", "args": ["mcp"] }
    }
  }
}
```

## HTTP Mode

```bash
qmd mcp --http              # Port 8181
qmd mcp --http --daemon     # Background
qmd mcp stop                # Stop daemon
```

## Tools

### structured_search

Search with pre-expanded queries.

```json
{
  "searches": [
    { "type": "lex", "query": "keyword phrases" },
    { "type": "vec", "query": "natural language question" },
    { "type": "hyde", "query": "hypothetical answer passage..." }
  ],
  "limit": 10,
  "collection": "optional",
  "minScore": 0.0
}
```

| Type | Method | Input |
|------|--------|-------|
| `lex` | BM25 | Keywords (2-5 terms) |
| `vec` | Vector | Question |
| `hyde` | Vector | Answer passage (50-100 words) |

### get

Retrieve document by path or `#docid`.

| Param | Type | Description |
|-------|------|-------------|
| `path` | string | File path or `#docid` |
| `full` | bool? | Return full content |
| `lineNumbers` | bool? | Add line numbers |

### multi_get

Retrieve multiple documents.

| Param | Type | Description |
|-------|------|-------------|
| `pattern` | string | Glob or comma-separated list |
| `maxBytes` | number? | Skip large files (default 10KB) |

### status

Index health and collections. No params.

## Troubleshooting

- **Not starting**: `which qmd`, `qmd mcp` manually
- **No results**: `qmd collection list`, `qmd embed`
- **Slow first search**: Normal, models loading (~3GB)
