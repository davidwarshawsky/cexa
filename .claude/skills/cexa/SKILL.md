---
name: cexa
description: Execute open-ended web searches and fetch webpage markdown via the remote Exa MCP service. Use when researching best practices, documentation, latest developments, or extracting clean markdown from webpages.
allowed-tools: Bash(*)
---

# Exa Remote MCP CLI (`cexa`)

`cexa` is a lightweight, token-efficient command-line interface to the official remote Exa MCP service (`https://mcp.exa.ai/mcp`).

Rather than configuring local MCP JSON files or dumping full MCP tool schemas into agent context up front, query `cexa` dynamically to discover tools, search the web, and retrieve clean webpage markdown.

## Pre-requisite / Installation Check

1. Verify `EXA_API_KEY` is set in the environment:
```bash
echo "${EXA_API_KEY:?EXA_API_KEY is not set. Run: export EXA_API_KEY='your-key'}"
```

2. Check if the CLI is available in the environment:
```bash
which cexa || command -v cexa || Get-Command cexa
```

**If `cexa` is not installed**, refer to [INSTALL.md](INSTALL.md) or install it immediately:
- **Fastest via `uv`:** `uv tool install git+https://github.com/davidwarshawsky/cexa`
- **On-the-fly execution via `uvx`:** prefix commands with `uvx --from git+https://github.com/davidwarshawsky/cexa cexa ...`
- **Via `pipx` or `pip`:** `pipx install git+https://github.com/davidwarshawsky/cexa.git` or `pip install git+https://github.com/davidwarshawsky/cexa.git`

## When to Use

Use `cexa` whenever you need:
- Current or up-to-date web information not present in local files or pre-training data
- Researching external libraries, frameworks, APIs, and release notes
- Finding blog posts, tutorials, and benchmark comparisons
- Clean Markdown extraction from one or more known URLs without browser overhead
- Autonomous agent research runs with multi-source synthesis

## Workflow & Commands

### 1. Discover Available Capabilities
Fetch available tools directly from the remote Exa MCP endpoint:
```bash
cexa --help
```

### 2. Inspect Tool Instructions On-Demand (Token Saver)
Retrieve the exact description, schema, and parameter guidance for a specific tool:
```bash
cexa --tool web_search_exa description
cexa --tool web_fetch_exa description
cexa --tool agent_run description
```

### 3. Neural Web Search
Search the web with Exa's neural search engine:
```bash
cexa search "<natural language description of ideal page>"
```

Provide search objective and result limits:
```bash
cexa search "uv python packaging best practices" --objective "Find how to structure pyproject.toml for cli tools" -n 5
```

### 4. Fetch Full Page Contents
Extract clean Markdown content from URLs:
```bash
cexa fetch "https://example.com/article" --max-chars 3000
```

Batch fetch multiple URLs:
```bash
cexa fetch "https://url1.com" "https://url2.com"
```

### 5. Call Any Tool Directly
Execute raw JSON tool calls against the Exa MCP server:
```bash
cexa call web_search_exa '{"query": "your query", "objective": "your objective", "numResults": 5}'
```
