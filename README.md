# cexa: Exa Remote MCP CLI Client

`cexa` is a lightweight, token-efficient command-line interface for the official remote [Exa MCP Server](https://mcp.exa.ai/mcp).

Rather than configuring cumbersome local MCP servers, managing json configs, or dumping hundreds of lines of MCP tool definitions into an AI agent's initial context window, `cexa` provides a clean CLI with dynamic tool discovery and inspection.

- **Zero third-party dependencies:** Implemented in pure Python 3 standard library (`urllib.request`, `json`, `argparse`).
- **Cross-platform:** Runs on macOS, Linux, and Windows.
- **Token-saver architecture:** Agents query only the tool descriptions they need when they need them.
- **Convenient shortcuts:** Dedicated `search` and `fetch` subcommands for rapid querying and scraping, as well as a generic `call` command for any current or future Exa MCP tool.

---

## Prerequisites

`cexa` requires an Exa API key. Get one from [Exa](https://dashboard.exa.ai/api-keys) and set it in your environment:

```bash
export EXA_API_KEY="your-exa-api-key"
```

On Windows PowerShell:
```powershell
$env:EXA_API_KEY="your-exa-api-key"
```

---

## Installation

### Option 1: Install with `uv` (Recommended)
```bash
uv tool install git+https://github.com/davidwarshawsky/cexa
```

### Option 2: Run directly with `uvx` (No install required)
```bash
uvx --from git+https://github.com/davidwarshawsky/cexa cexa --help
```

### Option 3: Install with `pipx`
```bash
pipx install git+https://github.com/davidwarshawsky/cexa.git
```

### Option 4: Install with `pip`
```bash
pip install git+https://github.com/davidwarshawsky/cexa.git
```

### Option 5: Local Clone & Editable Install
```bash
git clone https://github.com/davidwarshawsky/cexa.git
cd cexa
pip install -e .
```

---

## Quick Verification

Check if `cexa` is installed and ready:

```bash
which cexa || command -v cexa || Get-Command cexa
```

Inspect tool list:
```bash
cexa --help
```

---

## Usage

### 1. Discover Tools Dynamically
Query the remote Exa MCP server for available tools:
```bash
cexa
```

### 2. Inspect Tool Instructions (Token Saver)
Read the schema and guidance for a specific tool only when you need it:
```bash
cexa --tool web_search_exa description
cexa --tool web_fetch_exa description
cexa --tool agent_run description
```

### 3. Neural Web Search
Perform high-quality semantic searches across the web:
```bash
cexa search "Python standard library async HTTP client"
```

With an explicit objective and custom result limit:
```bash
cexa search "latest Claude 3.7 Sonnet hybrid reasoning benchmarks" --objective "Find performance comparisons with Claude 3.5 Sonnet and o3-mini" -n 5
```

Return raw JSON for programmatic parsing:
```bash
cexa search "AI coding benchmarks 2026" --json
```

### 4. Fetch Webpage Content as Markdown
Cleanly scrape web content and extract Markdown:
```bash
cexa fetch "https://docs.python.org/3/library/urllib.request.html" --max-chars 4000
```

Batch fetch multiple URLs in a single call:
```bash
cexa fetch "https://example.com/page1" "https://example.com/page2"
```

### 5. Generic MCP Tool Caller
Invoke any Exa MCP tool directly using JSON arguments:
```bash
cexa call web_search_exa '{"query": "machine learning developments 2026", "objective": "summarize key breakthroughs", "numResults": 5}'
```

---

## Agent Skills Support

Ready-to-use agent skills are included in this repository:
- **GitHub Copilot:** `.github/skills/cexa/`
- **Claude Code:** `.claude/skills/cexa/`
- **OpenAI Codex:** `.codex/skills/cexa/`
- **Agents Standard:** `.agents/skills/cexa/`

Each skill directory includes a self-contained `INSTALL.md` and pre-flight checks in `SKILL.md` so that AI agents can detect if `cexa` is missing, install it automatically, and run search tasks without human intervention.

---

# TLS / Enterprise CA Certificates

`cexa` always verifies HTTPS certificates. If your network uses an enterprise TLS inspection proxy, provide its trusted CA bundle through the standard Python environment variables:

```powershell
$env:SSL_CERT_FILE = 'C:\path\to\corporate-ca-bundle.pem'
# Or use a directory containing hashed CA certificates:
$env:SSL_CERT_DIR = 'C:\path\to\corporate-ca-directory'
```

Set these variables before running `cexa`. Do not disable certificate verification. If validation fails, the CLI reports that `SSL_CERT_FILE` or `SSL_CERT_DIR` can be set.
## License

MIT
