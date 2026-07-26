"""AI answer generation using Claude."""
import json
import re
import anthropic
from config import ANTHROPIC_API_KEY, MODEL
from parser import FormQuestion


def _build_prompt(questions: list[FormQuestion], context: str, form_title: str = "") -> str:
    q_lines = []
    for q in questions:
        line = f"[Q{q.index+1}] ({q.qtype}{'*' if q.required else ''}) {q.text}"
        if q.options:
            line += f"\n  Options: {', '.join(q.options)}"
        if q.qtype == "scale":
            line += f"\n  Scale: {q.scale_min}–{q.scale_max}"
        q_lines.append(line)

    context_section = f"""
<context>
{context.strip()}
</context>
""" if context else ""

    return f"""You are an expert form-filling assistant. Fill out this form accurately.

{context_section}
<form title="{form_title}">
{chr(10).join(q_lines)}
</form>

Return ONLY a JSON object where each key is the question number (1-indexed) and the value is the answer.

Rules:
- For "radio": return exactly ONE option string from the Options list
- For "checkbox": return a JSON array of selected option strings
- For "dropdown": return exactly ONE option string from the Options list
- For "scale": return a number between min and max as a string
- For "text"/"textarea"/"email"/"number": return the answer string
- For "date": return in YYYY-MM-DD format
- For "time": return in HH:MM format
- If required (*) and no context, make a reasonable answer
- Keep text/textarea answers concise and natural

Example output:
{{"1": "John Doe", "2": "Option A", "3": ["Choice 1", "Choice 3"], "4": "4", "5": "I prefer this because..."}}

Answer now:"""


def generate_answers(questions: list[FormQuestion], context: str = "", form_title: str = "") -> dict[str, str | list]:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY=your_key")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = _build_prompt(questions, context, form_title)

    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = msg.content[0].text.strip()

    # Extract JSON from response
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if not json_match:
        raise ValueError(f"AI response not valid JSON:\n{raw}")

    answers = json.loads(json_match.group())
    return answers
