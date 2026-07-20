#!/bin/bash
# XC Agent — one-shot setup
# Usage: bash agents/setup.sh

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$DIR")"

M='\033[95m'; G='\033[92m'; Y='\033[93m'; R='\033[91m'; C='\033[96m'; DIM='\033[2m'; RST='\033[0m'

echo -e "${M}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ⚡ XC AGENT · SETUP · AGENTIC AI ORCHESTRATOR      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${RST}"

# ── check python ─────────────────────────────────────────────────────────────
if ! command -v python3 >/dev/null 2>&1; then
  echo -e "${R}✗${RST} python3 not found. Install first."
  exit 1
fi
PYVER=$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
echo -e "${G}✓${RST} python3 ${PYVER}"

# ── install deps ─────────────────────────────────────────────────────────────
echo -e "${DIM}→ installing anthropic SDK...${RST}"
if pip install --quiet -r "$DIR/requirements.txt" 2>/dev/null; then
  echo -e "${G}✓${RST} deps installed"
elif pip install --quiet --user -r "$DIR/requirements.txt" 2>/dev/null; then
  echo -e "${G}✓${RST} deps installed (--user)"
elif pip install --quiet --break-system-packages -r "$DIR/requirements.txt" 2>/dev/null; then
  echo -e "${G}✓${RST} deps installed (--break-system-packages)"
else
  echo -e "${Y}⚠${RST} pip install failed. Try manually:"
  echo -e "  ${C}pip install anthropic${RST}"
fi

# ── check API key ────────────────────────────────────────────────────────────
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo -e "${Y}⚠${RST}  ANTHROPIC_API_KEY belum di-set."
  echo -e "  Get key: ${C}https://console.anthropic.com/settings/keys${RST}"
  echo -e "  Set: ${C}export ANTHROPIC_API_KEY=sk-ant-...${RST}"
  echo -e "  Persist: append ke ~/.bashrc atau ~/.zshrc"
else
  echo -e "${G}✓${RST} ANTHROPIC_API_KEY set"
fi

# ── smoke test ───────────────────────────────────────────────────────────────
echo -e "${DIM}→ smoke test tool_registry...${RST}"
if python3 "$DIR/tool_registry.py" --list >/dev/null 2>&1; then
  COUNT=$(python3 "$DIR/tool_registry.py" --list 2>/dev/null | tail -1 | awk '{print $2}')
  echo -e "${G}✓${RST} tool_registry OK — ${COUNT} tools registered"
else
  echo -e "${R}✗${RST} tool_registry BROKEN"
  exit 1
fi

echo -e "${DIM}→ smoke test agent CLI...${RST}"
if python3 "$DIR/xc_agent.py" --list-modes >/dev/null 2>&1; then
  MODES=$(python3 "$DIR/xc_agent.py" --list-modes 2>/dev/null | wc -l)
  echo -e "${G}✓${RST} xc_agent OK — ${MODES} workflows loaded"
else
  echo -e "${R}✗${RST} xc_agent BROKEN"
  exit 1
fi

echo
echo -e "${M}╔══════════════════════════════════════════════════════╗${RST}"
echo -e "${M}║${RST}  ${G}✓ SETUP DONE${RST}  ·  ready to gas 🔥                     ${M}║${RST}"
echo -e "${M}╚══════════════════════════════════════════════════════╝${RST}"
echo
echo -e "  ${C}QUICK START${RST}"
echo -e "  ${DIM}────────────${RST}"
echo -e "    ${G}python3 agents/xc_agent.py${RST}                              # REPL"
echo -e "    ${G}python3 agents/xc_agent.py --mode hack \"target.com\"${RST}      # hacking chain"
echo -e "    ${G}python3 agents/xc_agent.py --mode dox \"username\"${RST}         # OSINT"
echo -e "    ${G}python3 agents/xc_agent.py --mode brain \"capture ide\"${RST}    # brain"
echo -e "    ${G}python3 agents/xc_agent.py --mode cheatdev \"auto farm RPG\"${RST} # cheatdev"
echo
echo -e "  ${C}MCP CONNECTOR${RST}"
echo -e "  ${DIM}──────────────${RST}"
echo -e "    Add ke Claude client config:"
echo -e "    ${DIM}\"xc-hub\": { \"command\": \"python3\", \"args\": [\"$DIR/mcp_server.py\"] }${RST}"
echo
