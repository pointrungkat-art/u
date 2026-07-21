"""Fill a form using Playwright based on AI-generated answers."""
import asyncio
from parser import FormQuestion


async def fill_google_forms(page, questions: list[FormQuestion], answers: dict):
    containers = await page.query_selector_all('[role="listitem"]')
    q_idx = 0
    for container in containers:
        title_el = await container.query_selector('[role="heading"], .M7eMe, .z12JJ')
        if not title_el:
            title_el = await container.query_selector('div[class*="freebirdFormviewerViewItemsItemItemTitle"]')
        if not title_el:
            continue
        title = (await title_el.inner_text()).strip()
        if not title:
            continue

        key = str(q_idx + 1)
        answer = answers.get(key)
        if answer is None:
            q_idx += 1
            continue

        q = questions[q_idx] if q_idx < len(questions) else None
        qtype = q.qtype if q else "text"

        try:
            if qtype in ("text", "textarea", "email", "number", "date", "time"):
                inp = await container.query_selector('input[type="text"], input[type="email"], input[type="number"], input[type="date"], input[type="time"], textarea')
                if inp:
                    await inp.click()
                    await inp.fill(str(answer))

            elif qtype == "radio" or qtype == "scale":
                radios = await container.query_selector_all('[role="radio"]')
                target = str(answer).strip()
                for radio in radios:
                    label = (await radio.get_attribute("aria-label") or await radio.inner_text() or "").strip()
                    if label == target or target in label:
                        await radio.click()
                        break

            elif qtype == "checkbox":
                selected = answer if isinstance(answer, list) else [answer]
                checkboxes = await container.query_selector_all('[role="checkbox"]')
                for cb in checkboxes:
                    label = (await cb.get_attribute("aria-label") or await cb.inner_text() or "").strip()
                    if any(s.strip() in label or label in s.strip() for s in selected):
                        checked = await cb.get_attribute("aria-checked")
                        if checked != "true":
                            await cb.click()

            elif qtype == "dropdown":
                dropdown = await container.query_selector('[role="listbox"]')
                if dropdown:
                    await dropdown.click()
                    await page.wait_for_timeout(300)
                    options = await page.query_selector_all('[role="option"]')
                    target = str(answer).strip()
                    for opt in options:
                        text = (await opt.inner_text()).strip()
                        if text == target or target in text:
                            await opt.click()
                            break
        except Exception as e:
            print(f"  [warn] Q{key} fill error: {e}")

        q_idx += 1
        await page.wait_for_timeout(150)


async def fill_generic(page, questions: list[FormQuestion], answers: dict):
    for q in questions:
        key = str(q.index + 1)
        answer = answers.get(key)
        if answer is None:
            continue

        sel = q.raw_selector
        if not sel:
            continue

        try:
            el = await page.query_selector(sel)
            if not el:
                continue

            if q.qtype in ("text", "textarea", "email", "number", "date", "time"):
                await el.fill(str(answer))

            elif q.qtype == "dropdown":
                await el.select_option(label=str(answer))

            elif q.qtype in ("radio", "checkbox"):
                # Find matching option by value
                name = await el.get_attribute("name")
                if name:
                    options = await page.query_selector_all(f'input[name="{name}"]')
                    target = str(answer).strip() if q.qtype == "radio" else answer
                    for opt in options:
                        val = await opt.get_attribute("value") or ""
                        label_el = await page.query_selector(f'label[for="{await opt.get_attribute("id") or ""}"]')
                        label_text = (await label_el.inner_text()).strip() if label_el else val
                        if q.qtype == "radio":
                            if label_text == target or val == target:
                                await opt.click()
                                break
                        else:
                            selected = target if isinstance(target, list) else [target]
                            if any(s.strip() in label_text or label_text in s.strip() for s in selected):
                                await opt.click()
        except Exception as e:
            print(f"  [warn] Q{key} fill error: {e}")

        await page.wait_for_timeout(100)


async def fill_form(page, platform: str, questions: list[FormQuestion], answers: dict):
    if platform == "google":
        await fill_google_forms(page, questions, answers)
    else:
        await fill_generic(page, questions, answers)


async def submit_form(page, platform: str):
    if platform == "google":
        submit_btn = await page.query_selector('[role="button"][jsname="M2UYVd"], div[jsname="M2UYVd"]')
        if not submit_btn:
            submit_btn = await page.query_selector('div[role="button"]:has-text("Submit")')
        if submit_btn:
            await submit_btn.click()
            await page.wait_for_timeout(2000)
            return True
    else:
        submit_btn = await page.query_selector('input[type="submit"], button[type="submit"], button:has-text("Submit")')
        if submit_btn:
            await submit_btn.click()
            await page.wait_for_timeout(2000)
            return True
    return False
