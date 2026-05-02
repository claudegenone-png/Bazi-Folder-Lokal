# -*- coding: utf-8 -*-
"""V5 CLI — End-to-end: input nama+tanggal+jam+gender → chart.json → ocr.json → subject.json → PDF.

Usage:
    python cli.py "Michele" "1995-07-22" "14:00" "F" --hanzi "米雪"
    python cli.py "Tommy" "1960-05-08" "22:15" "M" --hanzi "湯米" --subject-id tommy
"""
from __future__ import annotations
import sys, json, argparse, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "engine"))

from compute_chart import compute as compute_chart
from chart_to_ocr import chart_to_ocr
from build_from_ocr import build_subject_from_ocr
from render import render_subject

GENDER_ID = {"M": "Pria", "F": "Wanita"}

def run(name, date, time_str, sex, hanzi, subject_id):
    t0 = time.time()
    y, mo, d = map(int, date.split("-"))
    h, mi = map(int, time_str.split(":"))
    sid = subject_id or name.lower().replace(" ", "")

    print(f"=== V5 Pipeline: {name} ({hanzi}) {date} {time_str} {sex} ===\n")

    # Step 1: compute chart.json
    t1 = time.time()
    print(f"[1/4] Compute chart.json (BaZi + Zi Wei via lunar-python + py-iztro)...")
    chart = compute_chart(name, y, mo, d, h, mi, sex)
    chart_path = ROOT / "data" / "subjects" / f"{sid}.chart.json"
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    chart_path.write_text(json.dumps(chart, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"      → {chart_path.name} ({time.time()-t1:.1f}s)\n")

    # Step 2: chart.json → ocr.json stub
    t2 = time.time()
    print(f"[2/4] Adapter chart.json → ocr.json (V4.5 format)...")
    # Pass user-provided hanzi (or None to trigger auto-gen in adapter)
    user_hanzi = None if (not hanzi or hanzi in ("?", "TBD", "")) else hanzi
    ocr = chart_to_ocr(chart, sid, name_hanzi=user_hanzi)
    ocr_path = ROOT / "data" / "subjects" / f"{sid}.ocr.json"
    ocr_path.write_text(json.dumps(ocr, ensure_ascii=False, indent=2), encoding="utf-8")
    final_hanzi = ocr["name_hanzi"]  # may be auto-generated
    print(f"      → {ocr_path.name} (hanzi={final_hanzi}) ({time.time()-t2:.1f}s)\n")

    # Step 3: ocr.json → subject.json
    t3 = time.time()
    print(f"[3/4] Build subject.json (Indonesian fields + lookup-driven narrative)...")
    build_subject_from_ocr(sid, name_id=name, name_hanzi=final_hanzi, gender_id=GENDER_ID[sex],
                           birth_date=date, birth_time=time_str)
    print(f"      → {sid}.json ({time.time()-t3:.1f}s)\n")

    # Step 4: render PDF
    t4 = time.time()
    print(f"[4/4] Render 23 HTML pages → PDF (Chrome headless)...")
    pdf_path = render_subject(sid)
    print(f"      ({time.time()-t4:.1f}s)\n")

    print(f"=== DONE in {time.time()-t0:.1f}s ===")
    print(f"PDF: {pdf_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="V5 — Yiteng-clone PDF pipeline (no photo)")
    ap.add_argument("name", help="Subject name (e.g. Michele)")
    ap.add_argument("date", help="Solar date YYYY-MM-DD")
    ap.add_argument("time", help="HH:MM")
    ap.add_argument("sex", choices=["M","F"])
    ap.add_argument("--hanzi", default="?", help="Chinese name (e.g. 米雪)")
    ap.add_argument("--subject-id", help="Optional subject id (defaults to lowercase name)")
    args = ap.parse_args()
    run(args.name, args.date, args.time, args.sex, args.hanzi, args.subject_id)
