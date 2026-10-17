
## Enterprise TLS certificates

The CLI verifies HTTPS certificates. For networks that use TLS inspection, set a trusted enterprise CA bundle before running it:

```powershell
$env:SSL_CERT_FILE = 'C:\path\to\corporate-ca-bundle.pem'
# Or use a directory containing hashed CA certificates:
$env:SSL_CERT_DIR = 'C:\path\to\corporate-ca-directory'
cexa --help
```

Keep certificate verification enabled. The variables are passed through automatically when `cexa` is launched from an MCP host.
# Installing `cexa`

The `cexa` CLI provides agents and developers with dynamic, token-efficient access to the remote Exa MCP Server (`https://mcp.exa.ai/mcp`).

It has **zero third-party dependencies** (uses only standard library Python 3) and runs seamlessly on Windows, macOS, and Linux.

---

## 1. Prerequisites: API Key

`cexa` requires the `EXA_API_KEY` environment variable:

```bash
export EXA_API_KEY="your-exa-api-key"
```

On Windows PowerShell:
```powershell
$env:EXA_API_KEY="your-exa-api-key"
```

---

## 2. Quick Verification

Before installing, check if `cexa` is already present in your PATH:

```bash
which cexa || command -v cexa || Get-Command cexa
```

Or test invocation directly:
```bash
cexa --help
```

---

## 3. Installation Options

### Option A: Install via `uv` (Recommended)
If `uv` is installed, install `cexa` as a globally isolated tool:
```bash
uv tool install git+https://github.com/davidwarshawsky/cexa
```

To update later:
```bash
uv tool upgrade cexa
```

---

### Option B: Run on the fly with `uvx` (No installation needed)
If you don't want to install anything permanently, run `cexa` on demand via `uvx`:
```bash
uvx --from git+https://github.com/davidwarshawsky/cexa cexa --help
```

---

### Option C: Install via `pipx`
If using `pipx`:
```bash
pipx install git+https://github.com/davidwarshawsky/cexa.git
```

---

### Option D: Install via `pip`
```bash
pip install git+https://github.com/davidwarshawsky/cexa.git
```

---

### Option E: Local Development / Clone
Clone the repository and install in editable mode:
```bash
git clone https://github.com/davidwarshawsky/cexa.git
cd cexa
pip install -e .
```
