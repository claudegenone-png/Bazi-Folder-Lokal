"""Mass replace Henry identity -> Michele identity across 23 pages.
Only touches identity (subject-bar, footer, cover) — does NOT touch tafsir/transcripts."""
import os, re
from pathlib import Path

DIR = Path(r"C:\temp\michele")

# Identity replacements (subject-bar, footer, cover)
REPLACEMENTS = [
    # Shio asset
    ('src="Harimau-Merah.svg"', 'src="Babi-Merah.svg"'),
    ('alt="Harimau"', 'alt="Babi"'),

    # SVG <image href> in wheel (compat page) — Michele's shio is Babi (亥), so wheel needs adjustment
    # but we'll handle that page separately

    # Subject-bar identity
    ('>Henry · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">寅 Harimau</span>',
     '>Michele · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">亥 Babi</span>'),

    # Day Master in subject-bar dm
    ('<div class="value">庚金 · Logam Yang</div>', '<div class="value">甲木 · Kayu Pohon Besar</div>'),

    # Footer meta
    ('<span>Henry · Ramalan 命</span>', '<span>Michele · Ramalan 命</span>'),

    # Cover-specific name
    ('<div class="cv-name">Henry</div>', '<div class="cv-name">Michele</div>'),

    # Subject details (common patterns)
    ('29 Oktober 1962 · 05:10 · Pria · Umur 64 tahun',
     '22 Juli 1995 · 14:48 · Wanita · Umur 30 tahun'),
    ('29 Oktober 1962 · 05:10 · Pria · 民國 51 年 10 月 2 日',
     '22 Juli 1995 · 14:48 · Wanita · 民國 84 年 6 月 25 日'),
    ('29 Oktober 1962 · 05:10 · Pria · Umur 64 · 大運 sekarang: <strong style="color:var(--red)">僕役 Friends</strong>',
     '22 Juli 1995 · 14:48 · Wanita · Umur 30 · 大運 sekarang: <strong style="color:var(--red)">己丑 (土)</strong>'),

    # Cover meta
    ('<span class="val">壬寅年 庚戌月<span class="id">29 Oktober 1962 · 05:10</span></span>',
     '<span class="val">乙亥年 癸未月<span class="id">22 Juli 1995 · 14:48</span></span>'),
    ('<span class="val">庚金 · 偏印格<span class="id">Logam Yang · Pian Yin Ge</span></span>',
     '<span class="val">甲木 · 傷官格<span class="id">Kayu Pohon Besar · Shang Guan Ge</span></span>'),

    # Title bar
    ('<title>Henry', '<title>Michele'),
]

count = 0
for page in sorted(DIR.glob("page_*.html")):
    html = page.read_text(encoding="utf-8")
    original = html
    for old, new in REPLACEMENTS:
        html = html.replace(old, new)
    if html != original:
        page.write_text(html, encoding="utf-8")
        count += 1

print(f"Updated identity in {count} pages")
