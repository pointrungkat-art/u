#!/usr/bin/env python3
"""Fill a form using pre-generated answers JSON."""
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/pw-browsers"

sys.path.insert(0, str(Path(__file__).parent))
from parser import parse_form, FormQuestion
from filler import fill_form, submit_form
from config import CHROMIUM_EXEC, SCREENSHOT_DIR

from playwright.async_api import async_playwright


async def run(url: str, answers: dict, do_submit: bool, screenshot: bool):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=CHROMIUM_EXEC,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = await browser.new_page()
        page.set_default_timeout(30000)

        print(f"Opening: {url}")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        platform, questions = await parse_form(page)
        print(f"Platform: {platform} | Questions: {len(questions)}")

        await fill_form(page, platform, questions, answers)
        print("Form filled!")

        if screenshot:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            ss = SCREENSHOT_DIR / f"filled_{ts}.png"
            await page.screenshot(path=str(ss), full_page=True)
            print(f"Screenshot: {ss}")

        if do_submit:
            ok = await submit_form(page, platform)
            if ok:
                print("SUBMITTED!")
                if screenshot:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ss = SCREENSHOT_DIR / f"submitted_{ts}.png"
                    await page.screenshot(path=str(ss), full_page=True)
                    print(f"Submit screenshot: {ss}")
            else:
                print("Submit button not found — filled but not submitted.")
        else:
            print("Fill only mode (no submit).")

        await page.wait_for_timeout(1000)
        await browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python autofill.py <url> <answers.json> [--submit] [--screenshot]")
        sys.exit(1)

    url = sys.argv[1]
    answers_path = sys.argv[2]
    do_submit = "--submit" in sys.argv
    screenshot = "--screenshot" in sys.argv

    answers = json.loads(Path(answers_path).read_text())
    asyncio.run(run(url, answers, do_submit, screenshot))
