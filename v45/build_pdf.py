"""V4.5 build+render shortcut (no OCR step).

Daily flow:
  1. Claude (di IDE) baca foto via Read tool, ekstrak data, tulis manual ke
     `data/subjects/{id}.ocr.json` (parallel batch Read — lihat AUTORUN.md).
  2. Run script ini: `python build_pdf.py <subject_id> [--name X --hanzi X --gender X --date YYYY-MM-DD --time HH:MM]`
  3. Output PDF ke `_pdf_out/{date}/{Name}-{Hanzi}-{Birth}-V4.5.pdf`
"""
import sys, time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "engines"))

from build_from_ocr import build_subject_from_ocr
from render import render_subject


def main():
    if len(sys.argv) < 2:
        print("Usage: python build_pdf.py <subject_id> "
              "[--name X --hanzi 漢字 --gender Pria --date YYYY-MM-DD --time HH:MM]")
        sys.exit(1)

    subject_id = sys.argv[1]
    args = sys.argv[2:]
    kw = {}
    for i, a in enumerate(args):
        if a == "--name" and i+1 < len(args): kw["name_id"] = args[i+1]
        elif a == "--hanzi" and i+1 < len(args): kw["name_hanzi"] = args[i+1]
        elif a == "--gender" and i+1 < len(args): kw["gender_id"] = args[i+1]
        elif a == "--date" and i+1 < len(args): kw["birth_date"] = args[i+1]
        elif a == "--time" and i+1 < len(args): kw["birth_time"] = args[i+1]

    t0 = time.time()
    print(f"=== Step 1: Build {subject_id}.json from {subject_id}.ocr.json ===")
    build_subject_from_ocr(subject_id, **kw)
    t1 = time.time()
    print(f"   Build: {t1-t0:.1f}s\n")

    print(f"=== Step 2: Render 23 pages → PDF ===")
    pdf = render_subject(subject_id)
    print(f"   Render+PDF: {time.time()-t1:.1f}s\n")
    print(f"DONE in {time.time()-t0:.1f}s: {pdf}")


if __name__ == "__main__":
    main()
