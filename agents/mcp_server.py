#!/usr/bin/env python3
"""XC Agent — MCP stdio server
Expose semua XC tools sebagai MCP tools. Zero external deps, pure stdio JSON-RPC.

Register di Claude client:
  {
    "mcpServers": {
      "xc-hub": {
        "command": "python3",
        "args": ["/absolute/path/to/agents/mcp_server.py"]
      }
    }
  }
"""

import json, sys, traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tool_registry import TOOLS, call_tool, list_tools_mcp  # noqa: E402

PROTO = "2025-06-18"
NAME = "xc-hub"
VERSION = "1.0.0"


def _reply(id_, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def _notify(method, params=None):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}}) + "\n")
    sys.stdout.flush()


def handle(req: dict):
    method = req.get("method")
    id_ = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        _reply(id_, {
            "protocolVersion": PROTO,
            "serverInfo": {"name": NAME, "version": VERSION},
            "capabilities": {"tools": {"listChanged": False}},
        })
        return

    if method == "notifications/initialized":
        return  # no response for notifications

    if method == "tools/list":
        _reply(id_, {"tools": list_tools_mcp()})
        return

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {}) or {}
        try:
            result = call_tool(name, args)
            content = [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]
            _reply(id_, {"content": content, "isError": not result.get("ok", True)})
        except Exception as e:
            tb = traceback.format_exc()
            _reply(id_, {"content": [{"type": "text", "text": f"{e}\n\n{tb}"}], "isError": True})
        return

    if method == "ping":
        _reply(id_, {})
        return

    if method == "shutdown":
        _reply(id_, {})
        sys.exit(0)

    if id_ is not None:
        _reply(id_, error={"code": -32601, "message": f"method not found: {method}"})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            handle(req)
        except Exception as e:
            sys.stderr.write(f"[mcp_server] handler crash: {e}\n{traceback.format_exc()}\n")


if __name__ == "__main__":
    main()
