"""Remove all English text where Indonesian translation already exists.
For English-only text, replace with Indonesian. Keep Pinyin (romanization)."""
import os, re
from pathlib import Path

DIR = Path(r"C:\temp\tommy")

# Order matters: do longer phrases first to avoid partial matches
REPLACEMENTS = [
    # Pillars
    ('Hour Pillar', 'Pilar Jam'),
    ('Day Pillar', 'Pilar Hari'),
    ('Month Pillar', 'Pilar Bulan'),
    ('Year Pillar', 'Pilar Tahun'),

    # Day Master
    ('★ DAY MASTER · 日主 ★', '★ 日主 · PENGUASA HARI ★'),
    ('DAY MASTER', 'PENGUASA HARI'),
    ('Day Master', 'Penguasa Hari'),

    # Yang Zhai zone names
    ('Mén · Doorway', 'Mén · Pintu Masuk'),
    ('Zào · Stove', 'Zào · Tungku Api'),
    ('Fáng · Room', 'Fáng · Kamar'),
    ('Chuáng · Bed', 'Chuáng · Ranjang'),
    ('Shén · Shrine', 'Shén · Tempat Pemujaan'),
    ('Cè · Toilet', 'Cè · Kamar Mandi'),

    # Status indicators
    ('FAVORABLE', 'MENDUKUNG'),
    ('UNFAVORABLE', 'WASPADA'),
    ('NEUTRAL', 'NETRAL'),
    ('STRONG', 'KUAT'),
    ('WEAK', 'LEMAH'),

    # 12 Palace English glosses
    ('CHILDREN', 'ANAK'),
    ('SPOUSE', 'PASANGAN'),
    ('SIBLINGS', 'SAUDARA'),
    ('FRIENDS', 'TEMAN'),
    ('TRAVEL', 'PERJALANAN'),
    ('CAREER', 'KARIR'),
    ('PROPERTY', 'PROPERTI'),
    ('HEALTH', 'KESEHATAN'),
    ('WEALTH', 'REZEKI'),
    ('KARMA', 'BERKAH'),
    ('PARENTS', 'ORANGTUA'),
    ('SELF', 'DIRI'),

    # Hua markers
    ('LIFE', 'HIDUP'),
    ('BODY', 'BADAN'),
    ('FAME', 'REPUTASI'),
    ('POWER', 'KUASA'),
    ('LUCK', 'BERKAH'),
    ('OBS', 'HALANG'),

    # Compass
    ('WEST GROUP', 'KELOMPOK BARAT'),
    ('EAST GROUP', 'KELOMPOK TIMUR'),

    # Trio cards
    ('Kekuatan · Power', 'Kekuatan'),
    ('Tantangan · Test', 'Tantangan'),
    ('Tindakan · Path', 'Tindakan'),

    # Headlines
    ('Big Picture', 'Gambaran Besar'),
    ('Big Number', 'Angka Utama'),

    # Synthesis
    ('Term Reference', 'Daftar Istilah'),
    ('Spouse', 'Pasangan'),
    ('Siblings', 'Saudara'),
    ('Children', 'Anak'),
    (' / Self', ' / Diri'),
    (' / Siblings', ' / Saudara'),
    (' / Spouse', ' / Pasangan'),
    (' / Children', ' / Anak'),
    (' / Wealth flow', ' / Aliran Rezeki'),
    (' / Health', ' / Kesehatan'),
    (' / Travel', ' / Perpindahan'),
    (' / Travel &amp; Change', ' / Perjalanan'),
    (' / Friends', ' / Teman'),
    (' / Friends &amp; Subordinates', ' / Pertemanan'),
    (' / Career', ' / Karir'),
    (' / Career &amp; Office', ' / Karir &amp; Jabatan'),
    (' / Property', ' / Properti'),
    (' / Karma', ' / Berkah'),
    (' / Parents', ' / Orangtua'),

    # Cycle labels
    ('★ ANDA · ', '★ ANDA · '),  # keep
    ('Cycle 6 of 10', 'Fase 6 dari 10'),
    ('Cycle 3 of 10', 'Fase 3 dari 10'),
    ('Sub Total', 'Sub Total'),  # keep, neutral
    ('Total', 'Total'),  # keep, used in both langs

    # Page section labels
    ('Section Opener', 'Pembuka Bab'),
    ('Section One', 'Bab Satu'),
    ('Section Two', 'Bab Dua'),

    # Time/Date words
    ('Born', 'Lahir'),
    ('Date', 'Tanggal'),
    ('Time', 'Waktu'),
    ('Solar', 'Masehi'),
    ('Lunar', 'Lunar'),  # keep, also Indonesian

    # Positions
    ('Past', 'Lalu'),
    ('Now', 'Sekarang'),
    ('Next', 'Berikutnya'),
    ('Future', 'Akan Datang'),
    (' END', ' SELESAI'),
    ('Halaman 23 / 23 · END', 'Halaman 23 / 23 · SELESAI'),

    # Misc English
    ('Action', 'Aksi'),
    ('Test', 'Ujian'),
    ('Path', 'Jalan'),
    ('Power', 'Kekuatan'),

    # Specific labels
    ('FIT', 'FIT'),  # keep, score abbreviation
    ('REPUTASI', 'REPUTASI'),
    ('Stable Income', 'Pendapatan Stabil'),
    ('Windfall', 'Rejeki Tak Terduga'),
    ('Stable', 'Stabil'),
    ('LUCK', 'KEBERUNTUNGAN'),

    # Star meanings (English glosses)
    ('Children · Stabilitas', 'Anak · Stabilitas'),
    ('Friends · Mentor', 'Teman · Mentor'),

    # Generic phrases
    ('Sì Huà', 'Sì Huà'),  # pinyin keep
    ('Five Elements', 'Lima Elemen'),
    ('BaZi Foundations', 'Dasar BaZi'),
    ('Zi Wei Main Stars', 'Bintang Utama Zi Wei'),
    ('12 Palaces (Zi Wei Houses)', '12 Istana Zi Wei'),
    ('Other Terms', 'Istilah Lain'),
    ('istilah', 'istilah'),

    # Tianyi noble helper etc
    ('Noble Helper', 'Penolong Terhormat'),
    ('Scholar', 'Cendekiawan'),
    ('General', 'Panglima'),
    ('Peach Blossom', 'Bunga Persik'),
    ('Canopy', 'Naungan Spiritual'),
    ('Robbery', 'Perampok'),
    ('Red Phoenix', 'Phoenix Merah'),
    ('Heavenly Virtue', 'Kebajikan Surgawi'),

    # Wu Xing English
    ('· Iron Bumi', '· Pohon Besar'),  # already Pohon, but cleanup
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

print(f"Removed English in {count} pages")
