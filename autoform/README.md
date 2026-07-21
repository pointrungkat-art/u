# AutoForm — AI Form Filler

Kasih URL form → AI baca soal → auto jawab → auto fill + submit.

## Setup

```bash
cd autoform
source .venv/bin/activate
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

```bash
# Review dulu (default — no submit)
python main.py "https://forms.gle/xxx"

# Auto-fill + submit
python main.py "https://forms.gle/xxx" --submit

# Pakai context file (profil/materi)
python main.py "https://forms.gle/xxx" --context context/profile.txt --submit

# Pakai PDF materi (ujian)
python main.py "https://forms.gle/xxx" --context materi.pdf --submit

# Inline context
python main.py "https://forms.gle/xxx" -i "Nama: Budi, Umur: 20, Jurusan: Teknik" --submit

# Save answers ke JSON + screenshot
python main.py "https://forms.gle/xxx" --submit --output answers.json --screenshot
```

## Flags

| Flag | Fungsi |
|------|--------|
| `--submit` | Auto-fill dan submit form |
| `--context file` | Path ke .txt atau .pdf sebagai context |
| `-i "..."` | Inline context string |
| `--output file.json` | Save jawaban ke JSON |
| `--screenshot` | Screenshot form (sebelum + sesudah submit) |
| `--no-headless` | Tampilkan browser window |

## Platform Support

- **Google Forms** ✓ (full support — radio, checkbox, dropdown, text, scale)
- **Typeform** (generic parser)
- **Microsoft Forms** (generic parser)
- **Any HTML form** (generic parser — label+input detection)
