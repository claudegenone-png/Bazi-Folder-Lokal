"""Round 2 — comprehensive English removal across all pages."""
import os, re
from pathlib import Path

DIR = Path(r"C:\temp\tommy")

REPLACEMENTS = [
    # SHIO English → Indonesian
    ('· Tiger', '· Harimau'),
    ('· Monkey', '· Monyet'),
    ('· Rat', '· Tikus'),
    ('· Ox', '· Kerbau'),
    ('· Snake', '· Ular'),
    ('· Horse', '· Kuda'),
    ('· Goat', '· Kambing'),
    ('· Rooster', '· Ayam'),
    ('· Dog', '· Anjing'),
    ('· Pig', '· Babi'),
    ('· Rabbit', '· Kelinci'),
    ('· Dragon', '· Naga'),
    ('>Tiger<', '>Harimau<'),
    ('>Monkey<', '>Monyet<'),
    ('>Rat<', '>Tikus<'),
    ('>Ox<', '>Kerbau<'),
    ('>Snake<', '>Ular<'),
    ('>Horse<', '>Kuda<'),
    ('>Goat<', '>Kambing<'),
    ('>Rooster<', '>Ayam<'),
    ('>Dog<', '>Anjing<'),
    ('>Pig<', '>Babi<'),
    ('>Rabbit<', '>Kelinci<'),
    ('>Dragon<', '>Naga<'),

    # Star catalog
    ('Star Catalog', 'Katalog Bintang'),
    ('Auspicious Stars', 'Bintang Berkah'),
    ('Auspicious/Inauspicious Stars', 'Bintang Berkah / Halangan'),
    ('Auspicious / Inauspicious', 'Berkah / Halangan'),

    # Lords & Palaces
    ('Life Lord / Body Lord', 'Penguasa Hidup / Penguasa Tubuh'),
    ('Life Lord', 'Penguasa Hidup'),
    ('Body Lord', 'Penguasa Tubuh'),
    ('Life Palace', 'Istana Hidup'),
    ('Body Palace', 'Istana Tubuh'),
    ('Friends Palace · Networking Era', 'Istana Pertemanan · Era Jejaring'),
    ('Friends Palace', 'Istana Pertemanan'),
    ('Networking Era', 'Era Jejaring'),

    # Career/Wealth/etc — title context (sí Shé · Wealth)
    ('· Wealth flow', '· Aliran Rezeki'),
    ('· Wealth', '· Rezeki'),
    ('· Career &amp; Office', '· Karir &amp; Jabatan'),
    ('· Career', '· Karir'),
    ('· Health', '· Kesehatan'),
    ('· Property', '· Properti'),
    ('· Travel &amp; Change', '· Perpindahan'),
    ('· Travel', '· Perpindahan'),
    ('· Friends &amp; Subordinates', '· Pertemanan &amp; Bawahan'),
    ('· Friends', '· Pertemanan'),
    ('· Children', '· Anak'),
    ('· Siblings', '· Saudara'),
    ('· Spouse', '· Pasangan'),
    ('· Parents', '· Orangtua'),
    ('· Karma', '· Berkah'),
    ('· Self', '· Diri'),

    # Glossary Wealth
    ('· Wealth flow', '· Aliran Rezeki'),
    ('Wealth flow', 'Aliran Rezeki'),

    # Page openers
    ('Self · Saudara · Pasangan · Anak', 'Diri · Saudara · Pasangan · Anak'),
    ('Wealth · Health · Travel · Friends', 'Rezeki · Kesehatan · Perpindahan · Pertemanan'),
    ('Career · Property · Karma · Parents', 'Karir · Properti · Berkah · Orangtua'),

    # 12 Palaces (Zi Wei Houses)
    ('12 Palaces (Zi Wei Houses)', '12 Istana Zi Wei'),

    # Specific English left
    ('Total Cai', 'Total Rezeki'),
    ('Total Wu Xing', 'Jumlah Wu Xing'),
    ('Insight Utama', 'Wawasan Utama'),
    ('Plus arah', 'Tambahan arah'),
    ('Toilet di arah', 'Kamar Mandi di arah'),
    ('favorable</strong>', 'mendukung</strong>'),
    ('unfavorable</strong>', 'kurang mendukung</strong>'),
    ('忌 Unfavorable', '忌 Kurang Mendukung'),
    ('Ji Shen · Unfavorable', 'Ji Shen · Kurang Mendukung'),
    ('Yong Shen · Favorable', 'Yong Shen · Mendukung'),

    # Stable income / windfall
    ('Stable Income', 'Pendapatan Stabil'),
    ('Windfall', 'Tak Terduga'),

    # Title bar tags (page_10, page_11)
    ('神煞 Star Catalog', '神煞 Katalog Bintang'),
    ('財富 Wealth', '財富 Rezeki'),

    # Five Elements / BaZi Foundations / etc (glossary)
    ('Five Elements', 'Lima Elemen'),
    ('BaZi Foundations', 'Dasar BaZi'),
    ('Zi Wei Main Stars', 'Bintang Utama Zi Wei'),
    ('Other Terms', 'Istilah Lain'),

    # Auxiliary
    ('Doorway', 'Pintu Masuk'),
    ('Stove', 'Tungku'),
    ('Bed', 'Ranjang'),
    ('Room', 'Kamar'),
    ('Shrine', 'Tempat Pemujaan'),
    ('Toilet', 'Kamar Mandi'),

    # Hour Pillar (in TOC)
    ('Four Pillars', 'Empat Pilar'),

    # 滴天髓 Lord glosses in glossary
    ('Mìng Zhǔ / Shēn Zhǔ', 'Mìng Zhǔ / Shēn Zhǔ'),  # keep pinyin

    # Star descriptions in shensha catalog
    ('Noble Helper', 'Penolong Mulia'),
    ('Scholar', 'Cendekiawan'),
    ('General', 'Jenderal'),
    ('Peach Blossom', 'Bunga Persik'),
    ('Canopy', 'Naungan Spiritual'),
    ('Robbery', 'Bencana Perampok'),
    ('Red Phoenix', 'Phoenix Merah'),
    ('Heavenly Virtue', 'Kebajikan Surgawi'),
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

print(f"Updated {count} pages")
