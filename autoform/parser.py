"""Extract questions from a form page using Playwright."""
import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FormQuestion:
    index: int
    text: str
    qtype: str          # text | textarea | radio | checkbox | dropdown | scale | date | time | email | number
    required: bool
    options: list[str] = field(default_factory=list)
    scale_min: int = 1
    scale_max: int = 5
    raw_selector: str = ""


async def detect_platform(page) -> str:
    url = page.url
    if "docs.google.com/forms" in url or "forms.gle" in url:
        return "google"
    if "typeform.com" in url:
        return "typeform"
    if "forms.office.com" in url or "forms.microsoft.com" in url:
        return "microsoft"
    return "generic"


async def parse_google_forms(page) -> list[FormQuestion]:
    questions = []
    # Google Forms question containers
    containers = await page.query_selector_all('[role="listitem"]')
    idx = 0
    for container in containers:
        # Question title
        title_el = await container.query_selector('[role="heading"], .M7eMe, .z12JJ')
        if not title_el:
            title_el = await container.query_selector('div[class*="freebirdFormviewerViewItemsItemItemTitle"]')
        if not title_el:
            continue
        title = (await title_el.inner_text()).strip()
        if not title:
            continue

        required = await container.query_selector('[aria-label*="Required"], [aria-required="true"]') is not None
        req_mark = await container.query_selector('.vnumgf')
        required = required or (req_mark is not None)

        # Detect type
        radio_els = await container.query_selector_all('[role="radio"]')
        check_els = await container.query_selector_all('[role="checkbox"]')
        dropdown_el = await container.query_selector('[role="listbox"], select')
        textarea_el = await container.query_selector('textarea')
        text_el = await container.query_selector('input[type="text"], input[type="email"], input[type="number"], input[type="date"], input[type="time"]')
        scale_el = await container.query_selector('[role="radiogroup"]')

        options = []
        qtype = "text"

        if radio_els:
            qtype = "radio"
            for r in radio_els:
                label = await r.get_attribute("aria-label") or await r.inner_text()
                if label.strip():
                    options.append(label.strip())
            # Check if it's a scale (linear scale)
            if scale_el and all(o.isdigit() for o in options):
                qtype = "scale"
        elif check_els:
            qtype = "checkbox"
            for c in check_els:
                label = await c.get_attribute("aria-label") or await c.inner_text()
                if label.strip():
                    options.append(label.strip())
        elif dropdown_el:
            qtype = "dropdown"
            option_els = await container.query_selector_all('[role="option"]')
            for o in option_els:
                t = await o.inner_text()
                if t.strip() and t.strip() != "Choose":
                    options.append(t.strip())
        elif textarea_el:
            qtype = "textarea"
        elif text_el:
            input_type = await text_el.get_attribute("type") or "text"
            qtype = input_type if input_type in ("email", "number", "date", "time") else "text"

        questions.append(FormQuestion(
            index=idx,
            text=title,
            qtype=qtype,
            required=required,
            options=options,
        ))
        idx += 1

    return questions


async def parse_generic(page) -> list[FormQuestion]:
    """Fallback parser for any HTML form."""
    questions = []
    idx = 0

    # Try to extract label + input pairs
    form_el = await page.query_selector("form") or page
    labels = await page.query_selector_all("label")

    handled_inputs = set()

    for label in labels:
        text = (await label.inner_text()).strip()
        if not text:
            continue

        # Find associated input
        for_attr = await label.get_attribute("for")
        input_el = None
        if for_attr:
            input_el = await page.query_selector(f"#{for_attr}")
        if not input_el:
            input_el = await label.query_selector("input, textarea, select")

        if not input_el:
            continue

        input_id = await input_el.get_attribute("id") or await input_el.get_attribute("name") or str(idx)
        if input_id in handled_inputs:
            continue
        handled_inputs.add(input_id)

        input_type = (await input_el.get_attribute("type") or "text").lower()
        tag = await input_el.evaluate("el => el.tagName.toLowerCase()")
        required = await input_el.get_attribute("required") is not None

        options = []
        qtype = "text"

        if tag == "select":
            qtype = "dropdown"
            option_els = await input_el.query_selector_all("option")
            for o in option_els:
                val = (await o.inner_text()).strip()
                if val:
                    options.append(val)
        elif tag == "textarea":
            qtype = "textarea"
        elif input_type == "radio":
            qtype = "radio"
            name = await input_el.get_attribute("name")
            if name:
                group = await page.query_selector_all(f'input[type="radio"][name="{name}"]')
                for r in group:
                    val = await r.get_attribute("value") or ""
                    r_label_el = await page.query_selector(f'label[for="{await r.get_attribute("id") or ""}"]')
                    label_text = (await r_label_el.inner_text()).strip() if r_label_el else val
                    if label_text:
                        options.append(label_text)
        elif input_type == "checkbox":
            qtype = "checkbox"
        elif input_type in ("email", "number", "date", "time"):
            qtype = input_type
        else:
            qtype = "text"

        questions.append(FormQuestion(
            index=idx,
            text=text,
            qtype=qtype,
            required=required,
            options=options,
            raw_selector=f'#{for_attr}' if for_attr else f'[name="{input_id}"]',
        ))
        idx += 1

    # If no labels found, try fieldset/legend or aria-label
    if not questions:
        inputs = await page.query_selector_all("input, textarea, select")
        for inp in inputs:
            aria = await inp.get_attribute("aria-label") or await inp.get_attribute("placeholder") or ""
            name = await inp.get_attribute("name") or ""
            text = aria or name
            if not text:
                continue
            tag = await inp.evaluate("el => el.tagName.toLowerCase()")
            input_type = (await inp.get_attribute("type") or "text").lower()
            qtype = "textarea" if tag == "textarea" else input_type if input_type in ("email", "number", "date") else "text"
            questions.append(FormQuestion(
                index=idx, text=text, qtype=qtype, required=False,
                raw_selector=f'[name="{name}"]' if name else "",
            ))
            idx += 1

    return questions


async def parse_form(page) -> tuple[str, list[FormQuestion]]:
    platform = await detect_platform(page)
    if platform == "google":
        questions = await parse_google_forms(page)
    else:
        questions = await parse_generic(page)
    return platform, questions
