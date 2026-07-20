"""XC Agent — Tool Registry
Catalog semua tools yang bisa dipanggil agent + MCP server.
Semua tool = subprocess wrapper ke tools/*.py, brain/data/*, cheatdev/forge/*.
"""

from __future__ import annotations
import json, os, subprocess, sys, time, uuid, re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
BRAIN_DATA = ROOT / "brain" / "data"
CHEATDEV_FORGE = ROOT / "cheatdev" / "forge" / "templates.lua"

for d in ("captures", "notes", "tasks", "journals", "runs"):
    (BRAIN_DATA / d).mkdir(parents=True, exist_ok=True)


def _run(cmd: list[str], timeout: int = 180) -> dict[str, Any]:
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        return {
            "ok": p.returncode == 0,
            "code": p.returncode,
            "stdout": p.stdout[-8000:],
            "stderr": p.stderr[-2000:],
            "elapsed": round(time.time() - t0, 2),
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": -1, "stdout": "", "stderr": f"timeout after {timeout}s", "elapsed": timeout}
    except FileNotFoundError as e:
        return {"ok": False, "code": -1, "stdout": "", "stderr": str(e), "elapsed": 0}


def _py(script: str, *args: str, timeout: int = 180) -> dict[str, Any]:
    path = TOOLS_DIR / script
    if not path.exists():
        return {"ok": False, "stderr": f"tool not found: {script}", "stdout": "", "code": -1, "elapsed": 0}
    return _run([sys.executable, str(path), *args], timeout=timeout)


def _read_json(p: Path, default):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def _write_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


# ── HACKING TOOLS ────────────────────────────────────────────────────────────

def tool_recon(target: str, full: bool = False) -> dict:
    args = [target] + (["--full"] if full else [])
    return _py("recon.py", *args, timeout=300)

def tool_ipfind(target: str, full: bool = False) -> dict:
    args = [target] + (["--full"] if full else [])
    return _py("ipfind.py", *args, timeout=240)

def tool_waf(target: str, full: bool = False) -> dict:
    args = [target] + (["--full"] if full else [])
    return _py("waf.py", *args, timeout=180)

def tool_cors(target: str, full: bool = False) -> dict:
    return _py("cors.py", target, *(["--full"] if full else []), timeout=180)

def tool_headers(target: str, full: bool = False) -> dict:
    return _py("headers.py", target, *(["--full"] if full else []), timeout=120)

def tool_jshunt(target: str, inline: bool = False) -> dict:
    return _py("js_hunt.py", target, *(["--inline"] if inline else []), timeout=240)

def tool_sqli(target: str, full: bool = False) -> dict:
    return _py("sqli.py", target, *(["--full"] if full else []), timeout=300)

def tool_ssti(target: str, rce: str | None = None) -> dict:
    args = [target] + (["--rce", rce] if rce else [])
    return _py("ssti.py", *args, timeout=240)

def tool_cmdi(target: str) -> dict:
    return _py("cmdi.py", target, timeout=240)

def tool_jwt(token: str, mode: str = "info") -> dict:
    return _py("jwt.py", token, "--" + mode, timeout=120)

def tool_ssrf(target: str) -> dict:
    return _py("ssrf.py", target, timeout=240)

def tool_upload(target: str) -> dict:
    return _py("upload.py", target, timeout=180)

def tool_stress(target: str, mode: str = "http", duration: int = 10) -> dict:
    return _py("stress.py", target, "--mode", mode, "--duration", str(duration), timeout=duration + 30)


# ── BRAIN TOOLS ──────────────────────────────────────────────────────────────

def _brain_file(name: str) -> Path:
    return BRAIN_DATA / f"{name}.json"

def brain_capture(text: str, type: str = "idea", tag: str = "") -> dict:
    items = _read_json(_brain_file("captures"), [])
    item = {
        "id": int(time.time() * 1000),
        "text": text,
        "type": type,
        "tag": tag,
        "processed": False,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    items.insert(0, item)
    _write_json(_brain_file("captures"), items)
    return {"ok": True, "captured": item}

def brain_get_captures(processed: bool | None = None, type: str | None = None, limit: int = 20) -> dict:
    items = _read_json(_brain_file("captures"), [])
    if processed is not None:
        items = [i for i in items if i.get("processed", False) == processed]
    if type:
        items = [i for i in items if i.get("type") == type]
    return {"ok": True, "count": len(items[:limit]), "items": items[:limit]}

def brain_create_task(title: str, desc: str = "", priority: str = "med", col: str = "todo") -> dict:
    tasks = _read_json(_brain_file("tasks"), [])
    task = {
        "id": int(time.time() * 1000),
        "title": title,
        "desc": desc,
        "priority": priority,
        "col": col,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    tasks.insert(0, task)
    _write_json(_brain_file("tasks"), tasks)
    return {"ok": True, "task": task}

def brain_get_tasks(col: str = "all", priority: str = "all") -> dict:
    tasks = _read_json(_brain_file("tasks"), [])
    if col != "all":
        tasks = [t for t in tasks if t.get("col") == col]
    if priority != "all":
        tasks = [t for t in tasks if t.get("priority") == priority]
    return {"ok": True, "count": len(tasks), "items": tasks}

def brain_update_task(id: int, col: str | None = None, priority: str | None = None, title: str | None = None) -> dict:
    tasks = _read_json(_brain_file("tasks"), [])
    for t in tasks:
        if t.get("id") == id:
            if col: t["col"] = col
            if priority: t["priority"] = priority
            if title: t["title"] = title
            _write_json(_brain_file("tasks"), tasks)
            return {"ok": True, "task": t}
    return {"ok": False, "error": f"task {id} not found"}

def brain_create_note(title: str, body: str = "", tags: list[str] | None = None) -> dict:
    notes = _read_json(_brain_file("notes"), [])
    note = {
        "id": int(time.time() * 1000),
        "title": title,
        "body": body,
        "tags": tags or [],
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    notes.insert(0, note)
    _write_json(_brain_file("notes"), notes)
    return {"ok": True, "note": note}

def brain_journal(text: str, mood: str = "neutral") -> dict:
    j = _read_json(_brain_file("journals"), [])
    entry = {
        "id": int(time.time() * 1000),
        "text": text,
        "mood": mood,
        "date": time.strftime("%Y-%m-%d"),
        "time": time.strftime("%H:%M"),
    }
    j.insert(0, entry)
    _write_json(_brain_file("journals"), j)
    return {"ok": True, "entry": entry}


# ── CHEATDEV FORGE ───────────────────────────────────────────────────────────

_TEMPLATE_CACHE: dict[str, str] | None = None

def _load_templates() -> dict[str, str]:
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is not None:
        return _TEMPLATE_CACHE
    out: dict[str, str] = {}
    if not CHEATDEV_FORGE.exists():
        _TEMPLATE_CACHE = out
        return out
    text = CHEATDEV_FORGE.read_text()
    pattern = re.compile(r"(\w+)\s*=\s*\[\[(.*?)\]\]", re.DOTALL)
    for m in pattern.finditer(text):
        out[m.group(1)] = m.group(2).strip()
    _TEMPLATE_CACHE = out
    return out

def cheatdev_list() -> dict:
    templates = _load_templates()
    return {"ok": True, "count": len(templates), "templates": sorted(templates.keys())}

def cheatdev_craft(name: str) -> dict:
    templates = _load_templates()
    key = name.upper()
    if key not in templates:
        return {"ok": False, "error": f"template '{name}' not found", "available": sorted(templates.keys())}
    return {"ok": True, "name": key, "loadstring": f'loadstring([[{templates[key]}]])()', "raw": templates[key]}

def cheatdev_save_raw(name: str, code: str) -> dict:
    saved_dir = BRAIN_DATA / "cheatdev_saved"
    saved_dir.mkdir(exist_ok=True)
    path = saved_dir / f"{name.upper()}.lua"
    path.write_text(code)
    return {"ok": True, "path": str(path.relative_to(ROOT)), "name": name.upper()}


# ── RUN LOG (agent trace) ────────────────────────────────────────────────────

def log_run(session_id: str, kind: str, payload: dict) -> None:
    p = BRAIN_DATA / "runs" / f"{session_id}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps({"ts": time.time(), "kind": kind, **payload}) + "\n")


# ── TOOL REGISTRY (name → (callable, schema)) ────────────────────────────────

TOOLS: dict[str, dict] = {
    # HACKING
    "recon": {
        "fn": tool_recon,
        "desc": "Full recon — DNS, HTTP, WAF, tech fingerprint, paths",
        "schema": {"type": "object", "properties": {
            "target": {"type": "string"}, "full": {"type": "boolean", "default": False}},
            "required": ["target"]},
    },
    "ipfind": {
        "fn": tool_ipfind,
        "desc": "Real IP hunter — CF bypass, DNS history, geo, ports",
        "schema": {"type": "object", "properties": {
            "target": {"type": "string"}, "full": {"type": "boolean", "default": False}},
            "required": ["target"]},
    },
    "waf": {
        "fn": tool_waf, "desc": "WAF detect + bypass",
        "schema": {"type": "object", "properties": {
            "target": {"type": "string"}, "full": {"type": "boolean", "default": False}}, "required": ["target"]},
    },
    "cors": {
        "fn": tool_cors, "desc": "CORS misconfiguration tester",
        "schema": {"type": "object", "properties": {
            "target": {"type": "string"}, "full": {"type": "boolean", "default": False}}, "required": ["target"]},
    },
    "headers": {
        "fn": tool_headers, "desc": "Security headers auditor + CSP",
        "schema": {"type": "object", "properties": {
            "target": {"type": "string"}, "full": {"type": "boolean", "default": False}}, "required": ["target"]},
    },
    "jshunt": {
        "fn": tool_jshunt, "desc": "JS secret harvester (API keys, tokens)",
        "schema": {"type": "object", "properties": {
            "target": {"type": "string"}, "inline": {"type": "boolean", "default": False}}, "required": ["target"]},
    },
    "sqli": {
        "fn": tool_sqli, "desc": "SQL injection fuzzer (error/boolean/time)",
        "schema": {"type": "object", "properties": {
            "target": {"type": "string"}, "full": {"type": "boolean", "default": False}}, "required": ["target"]},
    },
    "ssti": {
        "fn": tool_ssti, "desc": "SSTI detection + RCE payload generator",
        "schema": {"type": "object", "properties": {
            "target": {"type": "string"}, "rce": {"type": "string"}}, "required": ["target"]},
    },
    "cmdi": {
        "fn": tool_cmdi, "desc": "Command injection fuzzer",
        "schema": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
    },
    "jwt": {
        "fn": tool_jwt, "desc": "JWT attacks — alg:none, brute, kid, RS256→HS256",
        "schema": {"type": "object", "properties": {
            "token": {"type": "string"},
            "mode": {"type": "string", "enum": ["info", "none", "brute", "kid"], "default": "info"}},
            "required": ["token"]},
    },
    "ssrf": {
        "fn": tool_ssrf, "desc": "SSRF probe + internal service scan",
        "schema": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
    },
    "upload": {
        "fn": tool_upload, "desc": "File upload bypass — ext/MIME/magic/SVG",
        "schema": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
    },
    "stress": {
        "fn": tool_stress, "desc": "Server stress test — http/l4/slowloris/amplify",
        "schema": {"type": "object", "properties": {
            "target": {"type": "string"},
            "mode": {"type": "string", "enum": ["http", "l4", "slowloris", "amplify"], "default": "http"},
            "duration": {"type": "integer", "default": 10}},
            "required": ["target"]},
    },
    # BRAIN
    "brain_capture": {
        "fn": brain_capture, "desc": "Capture idea/task/resource ke Second Brain inbox",
        "schema": {"type": "object", "properties": {
            "text": {"type": "string"},
            "type": {"type": "string", "enum": ["idea", "task", "resource", "bug", "script", "vuln", "quote"], "default": "idea"},
            "tag": {"type": "string", "default": ""}},
            "required": ["text"]},
    },
    "brain_get_captures": {
        "fn": brain_get_captures, "desc": "List captures dari inbox",
        "schema": {"type": "object", "properties": {
            "processed": {"type": "boolean"},
            "type": {"type": "string"},
            "limit": {"type": "integer", "default": 20}}},
    },
    "brain_create_task": {
        "fn": brain_create_task, "desc": "Create task di kanban board",
        "schema": {"type": "object", "properties": {
            "title": {"type": "string"}, "desc": {"type": "string", "default": ""},
            "priority": {"type": "string", "enum": ["high", "med", "low"], "default": "med"},
            "col": {"type": "string", "enum": ["todo", "doing", "review", "done"], "default": "todo"}},
            "required": ["title"]},
    },
    "brain_get_tasks": {
        "fn": brain_get_tasks, "desc": "List tasks di kanban",
        "schema": {"type": "object", "properties": {
            "col": {"type": "string", "default": "all"}, "priority": {"type": "string", "default": "all"}}},
    },
    "brain_update_task": {
        "fn": brain_update_task, "desc": "Update task — move col / change priority / edit title",
        "schema": {"type": "object", "properties": {
            "id": {"type": "integer"}, "col": {"type": "string"},
            "priority": {"type": "string"}, "title": {"type": "string"}},
            "required": ["id"]},
    },
    "brain_create_note": {
        "fn": brain_create_note, "desc": "Buat note baru di Second Brain",
        "schema": {"type": "object", "properties": {
            "title": {"type": "string"}, "body": {"type": "string", "default": ""},
            "tags": {"type": "array", "items": {"type": "string"}}},
            "required": ["title"]},
    },
    "brain_journal": {
        "fn": brain_journal, "desc": "Tulis journal entry",
        "schema": {"type": "object", "properties": {
            "text": {"type": "string"},
            "mood": {"type": "string", "default": "neutral"}},
            "required": ["text"]},
    },
    # CHEATDEV
    "cheatdev_list": {
        "fn": cheatdev_list, "desc": "List semua Lua templates di cheatdev/forge",
        "schema": {"type": "object", "properties": {}},
    },
    "cheatdev_craft": {
        "fn": cheatdev_craft, "desc": "Craft Lua script dari template — return loadstring ready",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "cheatdev_save_raw": {
        "fn": cheatdev_save_raw, "desc": "Save raw Lua code ke brain/data/cheatdev_saved/",
        "schema": {"type": "object", "properties": {
            "name": {"type": "string"}, "code": {"type": "string"}},
            "required": ["name", "code"]},
    },
}


def get_tool(name: str):
    entry = TOOLS.get(name)
    if not entry:
        return None
    return entry["fn"]


def list_tools(subset: list[str] | None = None) -> list[dict]:
    """Return tool defs in Anthropic tool-format."""
    out = []
    for name, entry in TOOLS.items():
        if subset and name not in subset:
            continue
        out.append({"name": name, "description": entry["desc"], "input_schema": entry["schema"]})
    return out


def list_tools_mcp(subset: list[str] | None = None) -> list[dict]:
    """Return tool defs in MCP tool-format."""
    out = []
    for name, entry in TOOLS.items():
        if subset and name not in subset:
            continue
        out.append({"name": name, "description": entry["desc"], "inputSchema": entry["schema"]})
    return out


def call_tool(name: str, args: dict) -> dict:
    fn = get_tool(name)
    if not fn:
        return {"ok": False, "error": f"unknown tool: {name}"}
    try:
        return fn(**args)
    except TypeError as e:
        return {"ok": False, "error": f"bad args: {e}"}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="XC tool registry — CLI probe")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--call")
    ap.add_argument("--args", default="{}", help="JSON args")
    a = ap.parse_args()
    if a.list:
        for t in list_tools():
            print(f"  {t['name']:22s} {t['description']}")
        print(f"\nTotal: {len(TOOLS)}")
    elif a.call:
        r = call_tool(a.call, json.loads(a.args))
        print(json.dumps(r, indent=2, default=str))
    else:
        ap.print_help()
