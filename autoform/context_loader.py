"""Load context from .txt or .pdf files."""
from pathlib import Path


def load_txt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def load_pdf(path: str) -> str:
    try:
        import pdfplumber
        text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
        return "\n".join(text)
    except Exception as e:
        return f"[PDF read error: {e}]"


def load_context(path: str | None) -> str:
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Context file not found: {path}")
    if p.suffix.lower() == ".pdf":
        return load_pdf(str(p))
    return load_txt(str(p))
