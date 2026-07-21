import os
from pathlib import Path

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-5"

PLAYWRIGHT_BROWSERS_PATH = "/opt/pw-browsers"
CHROMIUM_EXEC = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

HEADLESS = True
TIMEOUT = 30000  # ms

CONTEXT_DIR = Path(__file__).parent / "context"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)
