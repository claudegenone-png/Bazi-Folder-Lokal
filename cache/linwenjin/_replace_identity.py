"""Mass replace Michele identity -> Lin Wen Jin identity across 23 pages.
Michele: 22 Juli 1995 14:48 / 乙亥 癸未 甲寅 辛未 / DM 甲木 / Babi
Lin Wen Jin: 27 Februari 1998 09:43 / 戊寅 甲寅 乙巳 辛巳 / DM 乙木 / Harimau
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DIR = Path(__file__).parent

# Order matters: longer / more specific first to avoid partial overlap.
REPLACEMENTS = [
    # ===== COVER CSS — widen panel + smaller font + nowrap rows so
    # "Tanggal Lahir (Indonesia)" / "Tanggal Lahir (Tionghoa)" labels muat 1 baris
    ('padding: 5mm 8mm;\n    margin: 4mm auto 0;\n    max-width: 130mm;',
     'padding: 5mm 9mm;\n    margin: 4mm auto 0;\n    max-width: 158mm;'),
    ('font-size: 10pt;\n    line-height: 1.7;',
     'font-size: 9pt;\n    line-height: 1.65;'),
    ('grid-template-columns: 36mm 4mm 1fr;\n    gap: 0;\n    align-items: baseline;\n  }',
     'grid-template-columns: 50mm 3mm 1fr;\n    gap: 0;\n    align-items: baseline;\n    white-space: nowrap;\n  }'),
    ('letter-spacing: 0.5px;\n    font-size: 9.5pt;\n  }\n  .cv-info-panel .colon',
     'letter-spacing: 0.3px;\n    font-size: 8.5pt;\n  }\n  .cv-info-panel .colon'),
    ('color: white;\n    font-weight: 500;\n  }\n  .cv-info-panel .val .hz',
     'color: white;\n    font-weight: 500;\n    overflow: hidden;\n    text-overflow: ellipsis;\n  }\n  .cv-info-panel .val .hz'),
    ('color: #E5D3A1; font-style: italic;\n    font-weight: 400; font-size: 9pt;',
     'color: #E5D3A1; font-style: italic;\n    font-weight: 400; font-size: 8pt;'),

    # ===== TITLE BAR =====
    ('<title>Michele', '<title>Lin Wen Jin'),

    # ===== SHIO ASSET =====
    ('src="Babi-Merah.svg"', 'src="Harimau-Merah.svg"'),
    ('src="Babi-Hitam.svg"', 'src="Harimau-Hitam.svg"'),
    ('alt="Babi"', 'alt="Harimau"'),

    # ===== SUBJECT-BAR identity =====
    ('Michele · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">亥 Babi</span>',
     'Lin Wen Jin · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">寅 Harimau</span>'),

    # ===== SUBJECT-DETAIL (long form) =====
    ('22 Juli 1995 · 14:48 · Wanita · 民國 84 年 6 月 25 日',
     '27 Februari 1998 · 09:43 · Pria · 民國 87 年 2 月 1 日'),
    ('22 Juli 1995 · 14:48 · Wanita · Umur 30 tahun',
     '27 Februari 1998 · 09:43 · Pria · Umur 28 tahun'),
    ('22 Juli 1995 · 14:48 · Wanita · Umur 30 · 大運 sekarang: <strong style="color:var(--red)">己丑 (土)</strong>',
     '27 Februari 1998 · 09:43 · Pria · Umur 28 · 大運 sekarang: <strong style="color:var(--red)">丁巳 (火)</strong>'),
    ('22 Juli 1995 · 14:48 · Wanita · Umur 30',
     '27 Februari 1998 · 09:43 · Pria · Umur 28'),

    # ===== SUBJECT-DM (Penguasa Hari) =====
    ('<div class="value">甲木 · Kayu Pohon Besar</div>',
     '<div class="value">乙木 · Kayu Yin (Tunas)</div>'),
    ('Penguasa Hari 甲木 (Kayu Yang)', 'Penguasa Hari 乙木 (Kayu Yin)'),
    ('Penguasa Hari 甲木', 'Penguasa Hari 乙木'),

    # ===== FOOTER =====
    ('<span>Michele · Ramalan 命</span>', '<span>Lin Wen Jin · Ramalan 命</span>'),

    # ===== COVER name =====
    ('<div class="cv-name">Michele</div>', '<div class="cv-name">Lin Wen Jin</div>'),
    ('<div class="cv-name-cn">米雪</div>', '<div class="cv-name-cn">林文進</div>'),

    # ===== COVER info-panel rows =====
    # Migrate Michele cover (3 baris: Tgl Lahir, Waktu, Kalender Lunar) →
    # Lin Wen Jin baseline (3 baris: Tgl Lahir Indonesia, Tgl Lahir Tionghoa, Waktu).
    # Label "Tanggal Lahir" lama jadi "Tanggal Lahir (Indonesia)";
    # Label "Kalender Lunar" lama jadi "Tanggal Lahir (Tionghoa)" + format "tanggal X bulan Y tahun GZ".
    ('<div class="row"><span class="lbl">Tanggal Lahir</span><span class="colon">:</span><span class="val">22 Juli 1995 <em>(Sabtu)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Waktu Lahir</span><span class="colon">:</span><span class="val">pukul 14:48 <em>(siang)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Kalender Lunar</span><span class="colon">:</span><span class="val">25 / bulan 6 / tahun Yi Hai <span class="hz">乙亥</span></span></div>',
     '<div class="row"><span class="lbl">Tanggal Lahir (Indonesia)</span><span class="colon">:</span><span class="val">27 Februari 1998 <em>(Jumat)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Tanggal Lahir (Tionghoa)</span><span class="colon">:</span><span class="val">tanggal 1 bulan 2 tahun <span class="hz">戊寅</span> <em>(Wu Yin · 1998)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Waktu Lahir</span><span class="colon">:</span><span class="val">pukul 09:43 <em>(pagi · 巳時)</em></span></div>'),
    # Fallback (kalau cover sudah versi 2-baris baru tapi data masih Michele):
    ('22 Juli 1995 <em>(Sabtu)</em>', '27 Februari 1998 <em>(Jumat)</em>'),
    ('pukul 14:48 <em>(siang)</em>', 'pukul 09:43 <em>(pagi · 巳時)</em>'),
    ('25 / bulan 6 / tahun Yi Hai <span class="hz">乙亥</span>',
     'tanggal 1 bulan 2 tahun <span class="hz">戊寅</span> <em>(Wu Yin · 1998)</em>'),
    ('<span class="hz">亥</span> Babi', '<span class="hz">寅</span> Harimau'),
    ('Kayu Pohon Besar <span class="hz">甲木</span>', 'Kayu Yin (Tunas) <span class="hz">乙木</span>'),
    ('Kayu &amp; Air <span class="hz">木 水</span>', 'Api &amp; Kayu <span class="hz">火 木</span>'),

    # ===== COVER metadata (year+month GZ) =====
    ('<span class="val">乙亥年 癸未月<span class="id">22 Juli 1995 · 14:48</span></span>',
     '<span class="val">戊寅年 甲寅月<span class="id">27 Februari 1998 · 09:43</span></span>'),
    ('<span class="val">甲木 · 傷官格<span class="id">Kayu Pohon Besar · Shang Guan Ge</span></span>',
     '<span class="val">乙木 · 劫財格<span class="id">Kayu Yin · Jie Cai Ge</span></span>'),

    # ===== CSS ::after content (cover badge) =====
    ("content: '亥 · BABI'", "content: '寅 · HARIMAU'"),

    # ===== Misc identity references =====
    ('Michele · Profil', 'Lin Wen Jin · Profil'),
    ('— Michele', '— Lin Wen Jin'),
    ('subjek: Michele', 'subjek: Lin Wen Jin'),
    ('Subjek: Michele', 'Subjek: Lin Wen Jin'),
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
        print(f"  updated: {page.name}")

# Also touch index.html
idx = DIR / "index.html"
if idx.exists():
    h = idx.read_text(encoding="utf-8")
    o = h
    for old, new in REPLACEMENTS:
        h = h.replace(old, new)
    if h != o:
        idx.write_text(h, encoding="utf-8")
        print(f"  updated: index.html")
        count += 1

print(f"\nUpdated identity in {count} files")
