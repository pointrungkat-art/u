# XC Agent — Agentic AI Orchestrator

Autonomous AI agent yang bungkus semua XC Hub tools (hacking, OSINT, brain, cheatdev)
jadi 1 CLI + MCP server. Hermes-style — kasih goal, agent chain tools sampe kelar.

## Quick Start

```bash
# Setup sekali aja
bash agents/setup.sh

# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Gas
python3 agents/xc_agent.py                                  # REPL
python3 agents/xc_agent.py --mode hack "shiroine.web.id"    # auto hack chain
python3 agents/xc_agent.py --mode dox "target"              # OSINT
python3 agents/xc_agent.py --mode brain "idea baru: ..."    # brain auto
python3 agents/xc_agent.py --mode cheatdev "auto farm RPG"  # Lua craft
```

## Modes

| Mode | Tools | Untuk apa |
|------|-------|-----------|
| `default` | Semua (23) | Generic — bebas apa aja |
| `hack` | 13 hacking + brain | Recon → exploit → report auto |
| `dox` | 4 recon + brain | OSINT compile DOX report |
| `brain` | 7 brain | Auto-classify capture/task/note/journal |
| `cheatdev` | 3 forge + brain | Craft Lua scripts + save |

## Tools Registered (23)

**Hacking:** `recon`, `ipfind`, `waf`, `cors`, `headers`, `jshunt`, `sqli`, `ssti`, `cmdi`, `jwt`, `ssrf`, `upload`, `stress`
**Brain:** `brain_capture`, `brain_get_captures`, `brain_create_task`, `brain_get_tasks`, `brain_update_task`, `brain_create_note`, `brain_journal`
**Cheatdev:** `cheatdev_list`, `cheatdev_craft`, `cheatdev_save_raw`

```bash
python3 agents/xc_agent.py --list-tools     # all 23
python3 agents/xc_agent.py --list-modes     # 5 workflows
python3 agents/tool_registry.py --list      # bare tool list
```

## MCP Server (untuk Claude Desktop / Cursor / Cline)

Tambahin ke config MCP client:

```json
{
  "mcpServers": {
    "xc-hub": {
      "command": "python3",
      "args": ["/absolute/path/to/agents/mcp_server.py"]
    }
  }
}
```

Zero external deps — stdio JSON-RPC pure Python.

## Files

```
agents/
├── xc_agent.py         # CLI entry — agentic loop
├── mcp_server.py       # MCP stdio server
├── tool_registry.py    # Central tool catalog (23 tools)
├── config.yaml         # Model, turns, defaults
├── setup.sh            # One-shot install
├── requirements.txt    # anthropic SDK
└── workflows/
    ├── default.yaml    # Generic
    ├── hack.yaml       # Auto hacking chain
    ├── dox.yaml        # OSINT DOX
    ├── brain.yaml      # Brain automation
    └── cheatdev.yaml   # Cheat forge
```

## Session Logs

Every agent run tersimpan ke `brain/data/runs/<session_id>.jsonl` — replay-able,
audit-able, cross-reference-able dari brain artifact.

## Env Vars

| Var | Default | Note |
|-----|---------|------|
| `ANTHROPIC_API_KEY` | — | Required |
| `XC_AGENT_MODEL` | `claude-sonnet-5` | Model override |
| `XC_AGENT_MAX_TURNS` | `20` | Max loop iterations |

## Extending

Add tool baru → edit `tool_registry.py`:

```python
def tool_myscan(target: str) -> dict:
    return _py("myscan.py", target)

TOOLS["myscan"] = {
    "fn": tool_myscan,
    "desc": "My custom scanner",
    "schema": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
}
```

Add workflow → drop YAML di `workflows/`:

```yaml
name: myflow
desc: Custom workflow
tools: [recon, myscan]
system: |
  You are MyFlow Agent...
```

Restart — auto discovered.
