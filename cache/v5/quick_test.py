# -*- coding: utf-8 -*-
"""V5 Quick Test — minimal input (nama + tanggal), auto-default time + gender, auto-open PDF."""
import sys, subprocess, os
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "engine"))

from cli import run

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python quick_test.py \"Nama\" \"YYYY-MM-DD\" [HH:MM] [M|F] [hanzi]")
        print("  Defaults: time=12:00, sex=M, hanzi=?")
        sys.exit(1)

    name = sys.argv[1]
    date = sys.argv[2]
    time_str = sys.argv[3] if len(sys.argv) > 3 else "12:00"
    sex = sys.argv[4] if len(sys.argv) > 4 else "M"
    hanzi = sys.argv[5] if len(sys.argv) > 5 else "?"

    print(f"Input: {name} | {date} | {time_str} | {sex} | {hanzi}\n")

    pdf_path = None
    # capture pdf path from cli.run
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run(name, date, time_str, sex, hanzi, None)
    output = buf.getvalue()
    print(output)
    # parse last "PDF: ..." line
    for line in reversed(output.splitlines()):
        if line.startswith("PDF: "):
            pdf_path = line[5:].strip()
            break

    if pdf_path and os.path.exists(pdf_path):
        print(f"\nOpening PDF in default viewer: {pdf_path}")
        os.startfile(pdf_path)  # Windows: opens in new window via default app
    else:
        print(f"\nPDF not found at: {pdf_path}")
