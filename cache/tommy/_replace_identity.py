"""Henry -> Tommy identity replacement."""
import os, re
from pathlib import Path

DIR = Path(r"C:\temp\tommy")

REPLACEMENTS = [
    # Shio asset (Henry: Harimau-Merah; Tommy: Tikus-Merah)
    ('src="Harimau-Merah.svg"', 'src="Tikus-Merah.svg"'),
    ('alt="Harimau"', 'alt="Tikus"'),

    # Subject-bar identity
    ('>Henry · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">寅 Harimau</span>',
     '>Tommy · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">子 Tikus</span>'),

    # Day Master in subject-dm (Henry: 庚金 Logam Yang; Tommy: 丙火 Api Matahari)
    ('<div class="value">庚金 · Logam Yang</div>',
     '<div class="value">丙火 · Api Matahari</div>'),

    # Footer meta
    ('<span>Henry · Ramalan 命</span>', '<span>Tommy · Ramalan 命</span>'),

    # Cover-specific name
    ('<div class="cv-name">Henry</div>', '<div class="cv-name">Tommy</div>'),

    # Subject-detail patterns (common)
    ('29 Oktober 1962 · 05:10 · Pria · Umur 64 tahun',
     '8 Mei 1960 · 22:15 · Pria · Umur 66 tahun'),
    ('29 Oktober 1962 · 05:10 · Pria · 民國 51 年 10 月 2 日',
     '8 Mei 1960 · 22:15 · Pria · 民國 49 年 4 月 13 日'),
    ('29 Oktober 1962 · 05:10 · Pria · Umur 64 · 大運 sekarang: <strong style="color:var(--red)">僕役 Friends</strong>',
     '8 Mei 1960 · 22:15 · Pria · Umur 66 · 大運 sekarang: <strong style="color:var(--red)">遷移 Perpindahan</strong>'),

    # Cover meta GanZhi (Henry 壬寅年 庚戌月; Tommy 庚子年 辛巳月)
    ('<span class="val">壬寅年 庚戌月<span class="id">29 Oktober 1962 · 05:10</span></span>',
     '<span class="val">庚子年 辛巳月<span class="id">8 Mei 1960 · 22:15</span></span>'),
    ('<span class="val">庚金 · 偏印格<span class="id">Logam Yang · Pian Yin Ge</span></span>',
     '<span class="val">丙火 · 正財格<span class="id">Api Matahari · Zheng Cai Ge</span></span>'),

    # Title bar
    ('<title>Henry', '<title>Tommy'),

    # Site-wide content (for tafsir text mentions of Day Master)
    ('庚金', '丙火'),
    ('Logam Yang', 'Api Matahari'),
    ('Iron Bumi', 'Matahari'),
    ('Gēng Jīn', 'Bǐng Huǒ'),

    # Format
    ('偏印格', '正財格'),
    ('Pian Yin Ge', 'Zheng Cai Ge'),
    ('Pencipta Mandiri', 'Pengelola Disiplin'),
    ('Pemikir Kreatif', 'Pengelola Disiplin'),

    # Yong Shen (Henry fav: 水 木 / unfav: 金 土; Tommy fav: 土 木 / unfav: 金 水)
    ('喜用神 水 木', '喜用神 土 木'),
    ('喜用神 水/木', '喜用神 土/木'),
    ('忌神 金 土', '忌神 金 水'),
    ('Air &amp; Kayu — Pengalir &amp; Penumbuh', 'Tanah &amp; Kayu — Penambat &amp; Penumbuh'),
    ('Logam &amp; Tanah — Penambah Dominasi', 'Logam &amp; Air — Pemadam Api Anda'),
    ('alirkan ke 水 木', 'tambatkan ke 土 木'),
    ('alirkan ke <span class="hz">水 木</span>', 'tambatkan ke <span class="hz">土 木</span>'),

    # Mantra (Henry 剛柔相濟; Tommy use different — for weak Bing, mantra: "守正待時" Shǒu Zhèng Dài Shí - hold steadfast wait the time)
    ('剛柔相濟', '守正待時'),
    ('Gāng Róu Xiāng Jì', 'Shǒu Zhèng Dài Shí'),
    ('Tegas dan lembut saling menyempurnakan', 'Pegang prinsip lurus, tunggu waktu yang tepat'),
    ('Halus dan tegas saling menyempurnakan', 'Pegang prinsip lurus, tunggu waktu yang tepat'),
    ('文武相濟', '守正待時'),
    ('Wén Wǔ Xiāng Jì', 'Shǒu Zhèng Dài Shí'),

    # Ziwei stars (Henry 廉貞/天梁; Tommy 破軍/火星)
    ('命主 廉貞', '命主 破軍'),
    ('身主 天梁', '身主 火星'),
    ('Lián Zhēn · Integritas', 'Pò Jūn · Pelopor'),
    ('Tān Láng · Hasrat Kreatif', 'Pò Jūn · Pelopor'),
    ('Tiān Liáng · Pelindung (身主)', 'Huǒ Xīng · Bintang Api (身主)'),
    ('Tiān Jī · Strategi (身主)', 'Huǒ Xīng · Bintang Api (身主)'),
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
