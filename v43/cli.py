"""V4.3 PRODUCTION CLI - End-to-end: photos folder -> subject.json -> 23 HTML pages -> PDF.

Usage:
    python cli.py <photos_dir> <subject_id> [--name X --hanzi 漢字 --gender Pria/Wanita --date YYYY-MM-DD --time HH:MM]

Pipeline:
  1. OCR all photos in folder -> data/subjects/{id}.ocr.json (cached per-photo)
  2. Build/update data/subjects/{id}.json from OCR + manual overrides
  3. Render 23 pages from JSON
  4. Build master HTML + Chrome -> PDF
  5. Output to OneDrive/Documents/Ramalan/#result/{date}/{Name}-{Hanzi}-{Birth}.pdf

Notes:
  - V4.3 = production daily render (alongside V3 manual flow di cache/{name}/)
  - User boleh pakai V3 ATAU V4.3 — keduanya output ke #result/ dengan naming sama
  - Steps 1-2 = pull-from-photo (no manual data entry)
  - Manual overrides for narrative tafsir live in data/subjects/{id}.overrides.json
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent

sys.path.insert(0, str(ROOT / "engines"))

# Load .env if present (so ANTHROPIC_API_KEY can be picked up without manual export)
import os as _os
_envf = ROOT / ".env"
if _envf.exists():
    for _line in _envf.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line: continue
        _k, _v = _line.split("=", 1)
        _os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from ocr import extract_subject as ocr_subject
from build_from_ocr import build_subject_from_ocr
from render import render_subject


def run(photos_dir: Path, subject_id: str, skip_ocr: bool = False, force_ocr: bool = False,
        name_id=None, name_hanzi=None, gender_id=None, birth_date=None, birth_time=None):
    import time as _time
    t0 = _time.time()
    if not skip_ocr:
        print(f"=== Step 1: OCR photos -> {subject_id}.ocr.json ===")
        ocr_subject(photos_dir, subject_id, force=force_ocr)
        print()

    print(f"=== Step 2: Auto-build {subject_id}.json from OCR + native pillars ===")
    build_subject_from_ocr(subject_id,
                           name_id=name_id, name_hanzi=name_hanzi,
                           gender_id=gender_id,
                           birth_date=birth_date, birth_time=birth_time)
    print()

    print(f"=== Step 3: Render 23 pages from {subject_id}.json ===")
    pdf_path = render_subject(subject_id)
    print()
    print(f"DONE in {_time.time()-t0:.1f}s: {pdf_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python cli.py <photos_dir> <subject_id> [--skip-ocr] [--force-ocr] "
              "[--name X --hanzi 漢字 --gender Pria --date YYYY-MM-DD --time HH:MM]")
        sys.exit(1)
    args = sys.argv[3:]
    kw = {}
    for i, a in enumerate(args):
        if a == "--name" and i+1 < len(args): kw["name_id"] = args[i+1]
        elif a == "--hanzi" and i+1 < len(args): kw["name_hanzi"] = args[i+1]
        elif a == "--gender" and i+1 < len(args): kw["gender_id"] = args[i+1]
        elif a == "--date" and i+1 < len(args): kw["birth_date"] = args[i+1]
        elif a == "--time" and i+1 < len(args): kw["birth_time"] = args[i+1]
    run(
        Path(sys.argv[1]),
        sys.argv[2],
        skip_ocr="--skip-ocr" in sys.argv,
        force_ocr="--force-ocr" in sys.argv,
        **kw,
    )
