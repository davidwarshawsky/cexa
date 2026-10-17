#!/usr/bin/env python3
"""cexa - CLI for the Exa Remote MCP Server.

Provides AI agents and command-line users with dynamic, token-efficient access
to Exa search and web page fetching via https://mcp.exa.ai/mcp.

Zero third-party dependencies — runs on standard library Python 3.
Requires EXA_API_KEY environment variable.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any

MCP_URL = "https://mcp.exa.ai/mcp"
USER_AGENT = "Mozilla/5.0 (compatible; cexa/0.1.0; +https://github.com/davidwarshawsky/cexa)"


def ssl_context() -> ssl.SSLContext:
    """Build a verified TLS context using optional CA environment overrides."""
    return ssl.create_default_context(
        cafile=os.environ.get("SSL_CERT_FILE") or None,
        capath=os.environ.get("SSL_CERT_DIR") or None,
    )


def get_api_key() -> str:
    """Retrieve EXA_API_KEY from environment or exit with error."""
    key = os.environ.get("EXA_API_KEY", "").strip()
    if not key:
        sys.stderr.write(
            "Error: EXA_API_KEY environment variable is not set.\n"
            "Please set it with: export EXA_API_KEY=\"your-key-here\"\n"
        )
        sys.exit(1)
    return key


def rpc_request(method: str, params: dict[str, Any] | None = None, api_key: str | None = None) -> dict[str, Any]:
    """Execute a JSON-RPC 2.0 request against the Exa MCP Server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {},
    }
    data = json.dumps(payload).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": USER_AGENT,
    }
    if api_key:
        headers["x-api-key"] = api_key

    req = urllib.request.Request(
        MCP_URL,
        data=data,
        headers=headers,
    )

    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl_context()) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(body)
            msg = err_json.get("error", {}).get("message") or err_json.get("detail") or body
        except Exception:
            msg = body
        sys.stderr.write(f"HTTP Error {exc.code} calling Exa MCP Server: {msg}\n")
        sys.exit(1)
    except urllib.error.URLError as exc:
        message = str(exc.reason)
        if "CERTIFICATE_VERIFY_FAILED" in message:
            message += " Set SSL_CERT_FILE or SSL_CERT_DIR to a trusted CA bundle."
        sys.stderr.write(f"Network error connecting to Exa MCP Server: {message}\n")
        sys.exit(1)
    except Exception as exc:
        sys.stderr.write(f"Unexpected error: {exc}\n")
        sys.exit(1)

    # Exa MCP server may return SSE streams ("event: message\ndata: {...}")
    cleaned = raw.strip()
    if cleaned.startswith("event:") or "data:" in cleaned:
        for line in cleaned.splitlines():
            line_stripped = line.strip()
            if line_stripped.startswith("data:"):
                json_part = line_stripped[len("data:"):].strip()
                try:
                    return json.loads(json_part)
                except Exception:
                    continue

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Failed to decode response from Exa MCP: {exc}\nRaw response:\n{raw}\n")
        sys.exit(1)


def list_tools() -> list[dict[str, Any]]:
    """List all available tools from the Exa MCP server."""
    # tools/list works even without an API key, but pass it if present
    api_key = os.environ.get("EXA_API_KEY", "").strip() or None
    res = rpc_request("tools/list", api_key=api_key)
    if "error" in res:
        sys.stderr.write(f"RPC Error listing tools: {res['error']}\n")
        sys.exit(1)
    return res.get("result", {}).get("tools", [])


def print_tool_description(tool_name: str, tools: list[dict[str, Any]]) -> None:
    """Print the documentation and parameter schema for a specific tool."""
    # Allow matching aliases without prefix
    target = tool_name.strip()
    match = None
    for t in tools:
        name = t.get("name", "")
        if name == target or name.removeprefix("web_").removesuffix("_exa") == target or name.replace("_exa", "") == target:
            match = t
            break

    if not match:
        available = [t.get("name") for t in tools]
        sys.stderr.write(f"Tool '{tool_name}' not found. Available tools: {', '.join(available)}\n")
        sys.exit(1)

    print(f"Tool: {match.get('name')}")
    print(f"\nDescription:\n{match.get('description', '').strip()}\n")
    print("Input Schema:")
    print(json.dumps(match.get("inputSchema", {}), indent=2))


def format_search_content(content_list: list[dict[str, Any]]) -> None:
    """Print search or fetch content in a readable terminal format."""
    for item in content_list:
        if isinstance(item, dict):
            text = item.get("text", "")
            if text:
                print(text)
            else:
                print(json.dumps(item, indent=2))
        else:
            print(str(item))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cexa",
        description=(
            "cexa - Token-efficient CLI for the Exa Remote MCP Server.\n\n"
            "Query web searches and fetch webpage content on demand without polluting\n"
            "agent context upfront. Requires EXA_API_KEY environment variable.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--tool",
        dest="tool_inspect",
        metavar="TOOL_NAME",
        help="Target tool name to inspect or run with an action (e.g. --tool web_search_exa description)",
    )
    parser.add_argument(
        "action",
        nargs="?",
        help="Action: 'description' (when used with --tool), 'call' (generic tool caller), 'search', or 'fetch'",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments for action (e.g., query, URLs, or JSON parameter string)",
    )

    # Convenience shortcuts for agent and human ease:
    # cexa search "query" [--objective OBJ] [--num-results N]
    # cexa fetch URL [URL2...] [--max-chars N]

    parsed, unknown = parser.parse_known_args()

    # 1. Handle tool inspection: cexa --tool <name> description
    if parsed.tool_inspect:
        action = (parsed.action or "").lower()
        if action == "description":
            tools = list_tools()
            print_tool_description(parsed.tool_inspect, tools)
            return
        elif action == "call":
            tool_name = parsed.tool_inspect
            api_key = get_api_key()
            args_str = " ".join(parsed.args) if parsed.args else "{}"
            try:
                call_args = json.loads(args_str) if args_str else {}
            except json.JSONDecodeError as exc:
                sys.stderr.write(f"Invalid JSON arguments: {exc}\n")
                sys.exit(1)

            res = rpc_request("tools/call", {"name": tool_name, "arguments": call_args}, api_key=api_key)
            if "error" in res:
                sys.stderr.write(f"RPC Error calling {tool_name}: {json.dumps(res['error'], indent=2)}\n")
                sys.exit(1)
            content = res.get("result", {}).get("content", [])
            format_search_content(content)
            return
        else:
            sys.stderr.write(f"Unknown action '{action}' for --tool {parsed.tool_inspect}. Use 'description' or 'call'.\n")
            sys.exit(1)

    # 2. No action or help requested -> List all available tools dynamically
    if not parsed.action or parsed.action in ("--help", "-h", "help"):
        tools = list_tools()
        print("Available tools from Exa MCP Server (https://mcp.exa.ai/mcp):\n")
        for t in tools:
            name = t.get("name", "unknown")
            desc = t.get("description", "").split("\n")[0].strip()
            print(f"  • {name:20} - {desc}")
        print("\nCommands & Workflows:")
        print("  1. Inspect tool schema:       cexa --tool <tool_name> description")
        print("  2. Perform neural web search: cexa search \"<query>\" [--objective \"<objective>\"] [-n 10]")
        print("  3. Fetch full webpage markdown: cexa fetch <url1> [url2...] [--max-chars 3000]")
        print("  4. Call any MCP tool raw:     cexa call <tool_name> '{\"arg\": \"val\"}'")
        print("\nEnvironment:")
        print("  EXA_API_KEY                   Required for 'search', 'fetch', and 'call'")
        return

    action_lower = parsed.action.lower()

    # 3. Direct tool caller: cexa call <tool_name> '{"key": "value"}'
    if action_lower == "call":
        if not parsed.args:
            sys.stderr.write("Usage: cexa call <tool_name> [json_arguments]\n")
            sys.exit(1)
        tool_name = parsed.args[0]
        # Resolve aliases
        if tool_name in ("search", "web_search"):
            tool_name = "web_search_exa"
        elif tool_name in ("fetch", "web_fetch"):
            tool_name = "web_fetch_exa"

        api_key = get_api_key()
        raw_args = " ".join(parsed.args[1:]) if len(parsed.args) > 1 else "{}"
        try:
            call_args = json.loads(raw_args) if raw_args.strip() else {}
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"Invalid JSON arguments: {exc}\n")
            sys.exit(1)

        res = rpc_request("tools/call", {"name": tool_name, "arguments": call_args}, api_key=api_key)
        if "error" in res:
            sys.stderr.write(f"RPC Error calling {tool_name}: {json.dumps(res['error'], indent=2)}\n")
            sys.exit(1)

        content = res.get("result", {}).get("content", [])
        format_search_content(content)
        return

    # 4. First-class Search command: cexa search "query" [--objective "..."] [-n 10]
    if action_lower == "search":
        search_parser = argparse.ArgumentParser(prog="cexa search", description="Search the web with Exa")
        search_parser.add_argument("query", help="Natural language search query")
        search_parser.add_argument("--objective", default=None, help="Goal for the search turn (rank order, excluded topics, facts to extract)")
        search_parser.add_argument("-n", "--num-results", type=int, default=10, help="Number of results (default: 10)")
        search_parser.add_argument("--json", action="store_true", help="Output raw JSON response")

        s_args = search_parser.parse_args(parsed.args + unknown)
        api_key = get_api_key()

        objective = s_args.objective or f"Find high quality, relevant information answering: {s_args.query}"
        params = {
            "query": s_args.query,
            "objective": objective,
            "numResults": s_args.num_results,
        }

        res = rpc_request("tools/call", {"name": "web_search_exa", "arguments": params}, api_key=api_key)
        if "error" in res:
            sys.stderr.write(f"Search error: {json.dumps(res['error'], indent=2)}\n")
            sys.exit(1)

        if s_args.json:
            print(json.dumps(res.get("result", {}), indent=2))
        else:
            content = res.get("result", {}).get("content", [])
            format_search_content(content)
        return

    # 5. First-class Fetch command: cexa fetch <url1> [url2...] [--max-chars 3000]
    if action_lower == "fetch":
        fetch_parser = argparse.ArgumentParser(prog="cexa fetch", description="Fetch full webpage content as markdown")
        fetch_parser.add_argument("urls", nargs="+", help="One or more URLs to fetch")
        fetch_parser.add_argument("--max-chars", type=int, default=3000, help="Max characters to extract per page (default: 3000)")
        fetch_parser.add_argument("--json", action="store_true", help="Output raw JSON response")

        f_args = fetch_parser.parse_args(parsed.args + unknown)
        api_key = get_api_key()

        params = {
            "urls": f_args.urls,
            "maxCharacters": f_args.max_chars,
        }

        res = rpc_request("tools/call", {"name": "web_fetch_exa", "arguments": params}, api_key=api_key)
        if "error" in res:
            sys.stderr.write(f"Fetch error: {json.dumps(res['error'], indent=2)}\n")
            sys.exit(1)

        if f_args.json:
            print(json.dumps(res.get("result", {}), indent=2))
        else:
            content = res.get("result", {}).get("content", [])
            format_search_content(content)
        return

    # If action is unrecognized
    sys.stderr.write(
        f"Unknown command: '{parsed.action}'.\n"
        "Run 'cexa' or 'cexa --help' to see available tools and commands.\n"
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
