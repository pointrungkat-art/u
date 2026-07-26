#!/usr/bin/env python3
"""
AutoForm — AI-powered form filler.
Usage: python main.py <form_url> [options]
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from playwright.async_api import async_playwright

# Add autoform dir to path
sys.path.insert(0, str(Path(__file__).parent))
from config import CHROMIUM_EXEC, PLAYWRIGHT_BROWSERS_PATH, HEADLESS, TIMEOUT, SCREENSHOT_DIR
from context_loader import load_context
from parser import parse_form
from ai import generate_answers
from filler import fill_form, submit_form

console = Console()
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = PLAYWRIGHT_BROWSERS_PATH


async def run(url: str, context_path: str | None, auto_submit: bool, headless: bool,
              output_json: str | None, screenshot: bool, inline_context: str | None):

    context_text = ""
    if inline_context:
        context_text = inline_context
    if context_path:
        console.print(f"[cyan]Loading context:[/] {context_path}")
        context_text = load_context(context_path)
        console.print(f"[green]✓[/] Context loaded — {len(context_text)} chars")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=CHROMIUM_EXEC,
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = await browser.new_page()
        page.set_default_timeout(TIMEOUT)

        console.print(f"\n[cyan]Opening form:[/] {url}")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # Get form title
        title_el = await page.query_selector("title")
        form_title = (await title_el.inner_text()).strip() if title_el else "Form"
        console.print(f"[green]✓[/] Form loaded: [bold]{form_title}[/]")

        # Parse form
        console.print("[cyan]Parsing questions...[/]")
        platform, questions = await parse_form(page)
        console.print(f"[green]✓[/] Platform: [bold]{platform}[/] | Questions found: [bold]{len(questions)}[/]")

        if not questions:
            console.print("[red]No questions found! The form might require login or use a different structure.[/]")
            await browser.close()
            return

        # Display questions
        table = Table(title="Questions Found", show_lines=True)
        table.add_column("No", style="cyan", width=4)
        table.add_column("Type", style="yellow", width=10)
        table.add_column("Required", width=8)
        table.add_column("Question")
        table.add_column("Options", style="dim")
        for q in questions:
            req = "✓" if q.required else ""
            opts = ", ".join(q.options[:4]) + ("..." if len(q.options) > 4 else "")
            table.add_row(str(q.index+1), q.qtype, req, q.text[:80], opts[:60])
        console.print(table)

        # Generate answers
        console.print("\n[cyan]Generating answers with AI...[/]")
        answers = generate_answers(questions, context_text, form_title)
        console.print("[green]✓[/] Answers generated\n")

        # Display answers
        ans_table = Table(title="AI Answers", show_lines=True)
        ans_table.add_column("No", style="cyan", width=4)
        ans_table.add_column("Question", width=40)
        ans_table.add_column("Answer", style="green")
        for q in questions:
            key = str(q.index + 1)
            ans = answers.get(key, "[no answer]")
            ans_str = json.dumps(ans, ensure_ascii=False) if isinstance(ans, list) else str(ans)
            ans_table.add_row(key, q.text[:40], ans_str[:80])
        console.print(ans_table)

        # Save JSON output
        if output_json:
            data = {
                "form_url": url,
                "form_title": form_title,
                "platform": platform,
                "generated_at": datetime.now().isoformat(),
                "questions": [{"index": q.index+1, "text": q.text, "type": q.qtype, "options": q.options} for q in questions],
                "answers": answers,
            }
            Path(output_json).write_text(json.dumps(data, indent=2, ensure_ascii=False))
            console.print(f"[green]✓[/] Answers saved → [bold]{output_json}[/]")

        # Review or auto-submit
        if not auto_submit:
            console.print(Panel(
                "[bold yellow]Review mode[/] — answers displayed above.\n"
                "Run with [bold cyan]--submit[/] to auto-fill and submit the form.",
                title="[yellow]Review Mode[/]"
            ))
            await browser.close()
            return

        # Fill form
        console.print("\n[cyan]Filling form...[/]")
        await fill_form(page, platform, questions, answers)
        console.print("[green]✓[/] Form filled!")

        if screenshot:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            ss_path = SCREENSHOT_DIR / f"filled_{ts}.png"
            await page.screenshot(path=str(ss_path), full_page=True)
            console.print(f"[green]✓[/] Screenshot → [bold]{ss_path}[/]")

        # Submit
        console.print("[cyan]Submitting...[/]")
        ok = await submit_form(page, platform)
        if ok:
            console.print("[bold green]✓ Form submitted successfully![/]")
            if screenshot:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                ss_path = SCREENSHOT_DIR / f"submitted_{ts}.png"
                await page.screenshot(path=str(ss_path), full_page=True)
                console.print(f"[green]✓[/] Submit screenshot → [bold]{ss_path}[/]")
        else:
            console.print("[yellow]⚠ Submit button not found — form filled but not submitted.[/]")

        await page.wait_for_timeout(1000)
        await browser.close()


@click.command()
@click.argument("url")
@click.option("--context", "-c", default=None, help="Path to context file (.txt or .pdf)")
@click.option("--inline-context", "-i", default=None, help="Inline context string")
@click.option("--submit", "auto_submit", is_flag=True, default=False, help="Auto-fill and submit the form")
@click.option("--no-headless", is_flag=True, default=False, help="Show browser window")
@click.option("--output", "-o", default=None, help="Save answers to JSON file")
@click.option("--screenshot", "-s", is_flag=True, default=False, help="Take screenshots")
def cli(url, context, inline_context, auto_submit, no_headless, output, screenshot):
    """AutoForm — AI-powered form filler.

    \b
    Examples:
      python main.py "https://forms.gle/xxx" --submit
      python main.py "https://forms.gle/xxx" --context profile.txt --submit --screenshot
      python main.py "https://forms.gle/xxx" -i "Nama: Budi, Umur: 20, Jurusan: Teknik"
      python main.py "https://forms.gle/xxx" --context materi.pdf --submit -o answers.json
    """
    asyncio.run(run(
        url=url,
        context_path=context,
        auto_submit=auto_submit,
        headless=not no_headless,
        output_json=output,
        screenshot=screenshot,
        inline_context=inline_context,
    ))


if __name__ == "__main__":
    cli()
