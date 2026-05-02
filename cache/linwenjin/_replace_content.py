"""Site-wide content replacement Henry -> Michele key terms.
This handles common terms in tafsir/transcripts; per-page nuance edits done separately."""
import os
from pathlib import Path

DIR = Path(r"C:\temp\michele")

# Common terms swap (Henry-specific -> Michele-equivalent)
REPLACEMENTS = [
    # Day Master references in tafsir
    ('庚金', '甲木'),
    ('Logam Yang', 'Kayu Yang'),
    ('Iron Bumi', 'Pohon Besar'),
    ('Gēng Jīn', 'Jiǎ Mù'),

    # Format
    ('偏印格', '傷官格'),
    ('Pian Yin Ge', 'Shang Guan Ge'),
    ('Pencipta Mandiri', 'Pemikir Kreatif'),

    # Yong Shen / Ji Shen labels (when standalone phrases)
    ('喜用神 水 木', '喜用神 火 金'),
    ('喜用神 水/木', '喜用神 火/金'),
    ('忌神 金 土', '忌神 水 木'),

    # Element direction context (when in tafsir)
    ('alirkan ke 水 木', 'salurkan ke 火 金'),
    ('alirkan ke <span class="hz">水 木</span>', 'salurkan ke <span class="hz">火 金</span>'),
    ('Air &amp; Kayu — Pengalir &amp; Penumbuh', 'Api &amp; Logam — Penyalur &amp; Pemangkas'),
    ('Logam &amp; Tanah — Penambah Dominasi', 'Air &amp; Kayu — Penambah Dominasi'),

    # Mantra
    ('剛柔相濟', '文武相濟'),  # different mantra: civic & martial
    ('Gāng Róu Xiāng Jì', 'Wén Wǔ Xiāng Jì'),
    ('Tegas dan lembut saling menyempurnakan', 'Halus dan tegas saling menyempurnakan'),

    # Henry-specific phrasings
    ('七殺 (Henry: 命主)', '貪狼 (Michele: 命主)'),
    ('Henry: 命主', 'Michele: 命主'),

    # Ziwei stars per Michele (vs Henry which had 廉貞/天梁)
    ('命主 廉貞', '命主 貪狼'),
    ('身主 天梁', '身主 天機'),
    ('Lián Zhēn · Integritas', 'Tān Láng · Hasrat Kreatif'),
    ('Tiān Liáng · Pelindung (身主)', 'Tiān Jī · Strategi (身主)'),
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

print(f"Updated content in {count} pages")
