#!/usr/bin/env python3
"""XC Agent — Agentic AI CLI (Claude SDK loop, Hermes-style autonomous)

Usage:
  python3 agents/xc_agent.py                          # interactive REPL
  python3 agents/xc_agent.py "recon shiroine.web.id"  # one-shot prompt
  python3 agents/xc_agent.py --mode hack "target.com" # workflow preset
  python3 agents/xc_agent.py --mode dox "target"
  python3 agents/xc_agent.py --mode brain "capture..."
  python3 agents/xc_agent.py --mode cheatdev "bikin auto-farm rpg"
  python3 agents/xc_agent.py --list-tools
  python3 agents/xc_agent.py --list-modes

Env:
  ANTHROPIC_API_KEY  (required — dari console.anthropic.com)
  XC_AGENT_MODEL     (default: claude-sonnet-5)
  XC_AGENT_MAX_TURNS (default: 20)
"""

from __future__ import annotations
import argparse, json, os, sys, time, uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tool_registry import TOOLS, call_tool, list_tools, log_run  # noqa: E402

# ── ANSI ─────────────────────────────────────────────────────────────────────
R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'
DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{M}
╔══════════════════════════════════════════════════════╗
║  ██╗  ██╗ ██████╗    █████╗  ██████╗ ███████╗███╗   ██╗████████╗ ║
║  ╚██╗██╔╝██╔════╝   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝ ║
║   ╚███╔╝ ██║        ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║    ║
║   ██╔██╗ ██║        ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║    ║
║  ██╔╝ ██╗╚██████╗   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║    ║
║  ╚═╝  ╚═╝ ╚═════╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝    ║
╠══════════════════════════════════════════════════════╣
║  ⚡ AGENTIC AI ORCHESTRATOR · CLAUDE SDK · HERMES-STYLE  ⚡      ║
╚══════════════════════════════════════════════════════╝{RST}
"""

DEFAULT_MODEL = os.environ.get("XC_AGENT_MODEL", "claude-sonnet-5")
DEFAULT_MAX_TURNS = int(os.environ.get("XC_AGENT_MAX_TURNS", "20"))


def load_workflows() -> dict[str, dict]:
    """Load workflow presets from agents/workflows/*.yaml (fallback to bundled defaults)."""
    wf_dir = Path(__file__).resolve().parent / "workflows"
    wfs: dict[str, dict] = {}
    if wf_dir.exists():
        for p in wf_dir.glob("*.yaml"):
            try:
                data = _tiny_yaml(p.read_text())
                if isinstance(data, dict) and "name" in data:
                    wfs[data["name"]] = data
            except Exception as e:
                print(f"{Y}[warn]{RST} skip workflow {p.name}: {e}", file=sys.stderr)
    return wfs


def _tiny_yaml(text: str) -> dict:
    """Minimal YAML parser — top-level keys, strings, lists. No nesting hell."""
    out: dict = {}
    current_key: str | None = None
    current_list: list | None = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()
        if not raw or raw.lstrip().startswith("#"):
            i += 1
            continue
        stripped = raw.lstrip()
        if stripped.startswith("- "):
            item = stripped[2:].strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(item)
            i += 1
            continue
        if ":" in stripped and not stripped.startswith(" "):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "|":
                block = []
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    if nxt.startswith("  ") or nxt.strip() == "":
                        block.append(nxt[2:] if nxt.startswith("  ") else nxt)
                        i += 1
                    else:
                        break
                out[key] = "\n".join(block).rstrip()
                current_key = None
                current_list = None
                continue
            if val == "":
                out[key] = []
                current_key = key
                current_list = out[key]
                i += 1
                continue
            out[key] = val.strip('"').strip("'")
            current_key = None
            current_list = None
        i += 1
    return out


def print_tool_call(name: str, args: dict):
    a = json.dumps(args, default=str)
    if len(a) > 200: a = a[:200] + "…"
    print(f"{DIM}  → {C}{name}{RST}{DIM}({a}){RST}")


def print_tool_result(name: str, result: dict):
    ok = result.get("ok", True)
    icon = f"{G}✓{RST}" if ok else f"{R}✗{RST}"
    summary = ""
    if "stdout" in result:
        first = (result["stdout"] or "").strip().splitlines()
        if first:
            summary = first[0][:120]
    elif "count" in result:
        summary = f"{result['count']} items"
    elif "captured" in result:
        summary = f"id={result['captured']['id']}"
    elif "task" in result:
        summary = f"task#{result['task']['id']} → {result['task']['col']}"
    elif "name" in result:
        summary = str(result["name"])
    print(f"  {icon} {DIM}{name}{RST} {DIM}· {summary}{RST}")


def run_agent(prompt: str, workflow: dict, model: str = DEFAULT_MODEL,
              max_turns: int = DEFAULT_MAX_TURNS, verbose: bool = True) -> dict:
    """Main agentic loop. Requires `anthropic` SDK installed."""
    try:
        from anthropic import Anthropic
    except ImportError:
        print(f"{R}✗{RST} anthropic SDK belum keinstall. Jalanin: {C}pip install anthropic pyyaml{RST}")
        print(f"  Atau: {C}bash agents/setup.sh{RST}")
        sys.exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{R}✗{RST} ANTHROPIC_API_KEY belum di-set.")
        print(f"  Set: {C}export ANTHROPIC_API_KEY=sk-ant-...{RST}")
        print(f"  Get key: {C}https://console.anthropic.com/settings/keys{RST}")
        sys.exit(1)

    client = Anthropic()
    session_id = uuid.uuid4().hex[:12]

    system = workflow.get("system", "You are XC Agent, an autonomous AI operator.")
    tool_subset = workflow.get("tools") or None
    tools = list_tools(tool_subset)

    if verbose:
        print(f"{DIM}session={session_id} · mode={workflow.get('name', 'default')} · model={model} · tools={len(tools)}{RST}\n")

    log_run(session_id, "start", {"workflow": workflow.get("name"), "prompt": prompt, "model": model})

    messages = [{"role": "user", "content": prompt}]
    turn = 0

    while turn < max_turns:
        turn += 1
        if verbose:
            print(f"{DIM}── turn {turn}/{max_turns} ──{RST}")

        try:
            resp = client.messages.create(
                model=model,
                max_tokens=4096,
                system=system,
                tools=tools,
                messages=messages,
            )
        except Exception as e:
            print(f"{R}✗ API error:{RST} {e}")
            log_run(session_id, "api_error", {"error": str(e)})
            return {"ok": False, "error": str(e), "session_id": session_id}

        assistant_content = resp.content
        messages.append({"role": "assistant", "content": assistant_content})

        tool_uses = [b for b in assistant_content if getattr(b, "type", None) == "tool_use"]
        text_blocks = [b for b in assistant_content if getattr(b, "type", None) == "text"]

        for tb in text_blocks:
            if tb.text.strip():
                print(f"{BOLD}{tb.text}{RST}")

        if resp.stop_reason == "end_turn" or not tool_uses:
            log_run(session_id, "end", {"turns": turn, "stop_reason": resp.stop_reason})
            if verbose:
                print(f"\n{G}✓ done{RST} {DIM}({turn} turns · session={session_id}){RST}")
            return {"ok": True, "turns": turn, "session_id": session_id}

        tool_results = []
        for tu in tool_uses:
            if verbose:
                print_tool_call(tu.name, dict(tu.input))
            result = call_tool(tu.name, dict(tu.input))
            log_run(session_id, "tool_call", {"name": tu.name, "args": dict(tu.input), "ok": result.get("ok", True)})
            if verbose:
                print_tool_result(tu.name, result)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": json.dumps(result, default=str)[:12000],
                "is_error": not result.get("ok", True),
            })

        messages.append({"role": "user", "content": tool_results})

    print(f"{Y}⚠ max_turns reached ({max_turns}){RST}")
    log_run(session_id, "max_turns", {"turns": turn})
    return {"ok": False, "error": "max_turns", "turns": turn, "session_id": session_id}


def cmd_interactive(workflows: dict):
    print(BANNER)
    print(f"  Type your goal, XC Agent akan orchestrate tools. {DIM}(/quit to exit, /mode <name> to switch){RST}\n")
    current = workflows.get("default") or next(iter(workflows.values()))
    print(f"  Mode: {G}{current['name']}{RST}  ·  Tools: {len(list_tools(current.get('tools')))}  ·  Model: {DEFAULT_MODEL}\n")
    while True:
        try:
            line = input(f"{M}xc-agent> {RST}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            continue
        if line in ("/quit", "/exit"):
            return
        if line.startswith("/mode "):
            name = line[6:].strip()
            if name in workflows:
                current = workflows[name]
                print(f"{G}✓{RST} switched to {G}{name}{RST}")
            else:
                print(f"{R}✗{RST} unknown mode. Available: {', '.join(workflows)}")
            continue
        if line == "/modes":
            for n, w in workflows.items():
                print(f"  {G}{n:12s}{RST} {DIM}{w.get('desc', '')}{RST}")
            continue
        if line == "/tools":
            for t in list_tools(current.get("tools")):
                print(f"  {C}{t['name']:22s}{RST} {DIM}{t['description']}{RST}")
            continue
        run_agent(line, current)


def cmd_oneshot(prompt: str, workflow: dict):
    print(BANNER)
    run_agent(prompt, workflow)


def main():
    ap = argparse.ArgumentParser(description="XC Agent — Agentic AI orchestrator")
    ap.add_argument("prompt", nargs="*", help="one-shot prompt (omit for REPL)")
    ap.add_argument("--mode", default="default", help="workflow preset")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    ap.add_argument("--list-tools", action="store_true")
    ap.add_argument("--list-modes", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    workflows = load_workflows()
    if not workflows:
        workflows["default"] = {"name": "default", "desc": "generic autonomous",
                                "system": "You are XC Agent. Use tools autonomously to accomplish the user's goal.",
                                "tools": None}

    if args.list_tools:
        for t in list_tools():
            print(f"  {t['name']:22s} {t['description']}")
        print(f"\nTotal: {len(TOOLS)}")
        return

    if args.list_modes:
        for n, w in workflows.items():
            print(f"  {n:12s} {w.get('desc', '')}")
        return

    workflow = workflows.get(args.mode)
    if not workflow:
        print(f"{R}✗{RST} unknown mode: {args.mode}. Available: {', '.join(workflows)}")
        sys.exit(1)

    if args.prompt:
        prompt = " ".join(args.prompt)
        cmd_oneshot(prompt, workflow)
    else:
        cmd_interactive(workflows)


if __name__ == "__main__":
    main()
