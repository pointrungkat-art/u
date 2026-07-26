#!/usr/bin/env python3
"""Extract questions from a form and dump as JSON — no API key needed."""
import asyncio
import json
import sys
import os
from pathlib import Path

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/pw-browsers"

sys.path.insert(0, str(Path(__file__).parent))
from parser import parse_form
from config import CHROMIUM_EXEC

from playwright.async_api import async_playwright


async def extract(url: str) -> dict:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=CHROMIUM_EXEC,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = await browser.new_page()
        page.set_default_timeout(30000)
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        title_el = await page.query_selector("title")
        form_title = (await title_el.inner_text()).strip() if title_el else "Form"

        platform, questions = await parse_form(page)
        await browser.close()

    return {
        "url": url,
        "title": form_title,
        "platform": platform,
        "questions": [
            {
                "no": q.index + 1,
                "text": q.text,
                "type": q.qtype,
                "required": q.required,
                "options": q.options,
            }
            for q in questions
        ],
    }


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if not url:
        print("Usage: python extract.py <url>")
        sys.exit(1)

    result = asyncio.run(extract(url))
    print(json.dumps(result, indent=2, ensure_ascii=False))
