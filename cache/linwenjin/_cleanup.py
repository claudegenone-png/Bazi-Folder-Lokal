"""Final cleanup — fix residue references to Michele/Henry/old format/old DM"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
DIR = Path(__file__).parent

REPL = [
    # Day Master + format global swap
    ('傷官格', '劫財格'),
    ('Shang Guan Ge', 'Jie Cai Ge'),
    ('甲木', '乙木'),
    ('Pohon Besar', 'Tunas Lentur'),
    ('Kayu Pohon Besar', 'Kayu Yin (Tunas)'),
    ('Kayu Yang', 'Kayu Yin'),
    ('Pencipta Kreatif', 'Pejuang Sejajar'),
    ('Pemikir Kreatif', 'Pejuang Sejajar'),

    # Henry leftovers
    (' Henry · Ramalan 命', ' Lin Wen Jin · Ramalan 命'),
    ('· Henry · Ramalan', '· Lin Wen Jin · Ramalan'),
    ('Henry · Ramalan', 'Lin Wen Jin · Ramalan'),
    ('untuk Henry', 'untuk Lin Wen Jin'),
    ("Henry's gua", "Trigram pribadi (Lin Wen Jin)"),
    ("Henry's NE-SW", "Lin Wen Jin's NE-SW"),
    ('Henry trait', 'Lin Wen Jin trait'),
    ('(Michele: 命主)', '(命主)'),

    # Michele references
    ('Michele:', ''),
]

count = 0
for page in sorted(DIR.glob("page_*.html")):
    h = page.read_text(encoding="utf-8")
    o = h
    for old, new in REPL:
        h = h.replace(old, new)
    if h != o:
        page.write_text(h, encoding="utf-8")
        count += 1
        print(f"  cleaned: {page.name}")
print(f"\n{count} files cleaned")
