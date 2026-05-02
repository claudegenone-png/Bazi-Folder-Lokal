"""Mass replace Michele identity -> Lin Ru Yi identity across 23 pages.
Michele:   22 Juli 1995 14:48 / 乙亥 癸未 甲寅 辛未 / DM 甲木 / Babi (亥) / 傷官格
Lin Ru Yi: 30 Mei 1995  10:35 / 乙亥 辛巳 辛酉 癸巳 / DM 辛金 / Babi (亥) / 正官格
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
DIR = Path(__file__).parent

REPLACEMENTS = [
    # ===== COVER CSS — widen panel + smaller font + nowrap rows =====
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

    # TITLE
    ('<title>Michele', '<title>Lin Ru Yi'),

    # SUBJECT-BAR
    ('Michele · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">亥 Babi</span>',
     'Lin Ru Yi · <span style="font-family:\'Noto Serif TC\',serif;color:var(--red)">亥 Babi</span>'),

    # Day Master subject-bar
    ('<div class="value">甲木 · Kayu Pohon Besar</div>',
     '<div class="value">辛金 · Logam Halus</div>'),

    # SUBJECT-DETAIL
    ('22 Juli 1995 · 14:48 · Wanita · 民國 84 年 6 月 25 日',
     '30 Mei 1995 · 10:35 · Wanita · 民國 84 年 5 月 2 日'),
    ('22 Juli 1995 · 14:48 · Wanita · Umur 30 tahun',
     '30 Mei 1995 · 10:35 · Wanita · Umur 30 tahun'),
    ('22 Juli 1995 · 14:48 · Wanita · Umur 30 · 大運 sekarang: <strong style="color:var(--red)">己丑 (土)</strong>',
     '30 Mei 1995 · 10:35 · Wanita · Umur 30 · 大運 sekarang: <strong style="color:var(--red)">甲申 (金)</strong>'),
    ('22 Juli 1995 · 14:48 · Wanita · Umur 30',
     '30 Mei 1995 · 10:35 · Wanita · Umur 30'),

    # FOOTER
    ('<span>Michele · Ramalan 命</span>', '<span>Lin Ru Yi · Ramalan 命</span>'),

    # COVER name
    ('<div class="cv-name">Michele</div>', '<div class="cv-name">Lin Ru Yi</div>'),
    ('<div class="cv-name-cn">米雪</div>', '<div class="cv-name-cn">林如意</div>'),

    # COVER info-panel rows
    ('<div class="row"><span class="lbl">Tanggal Lahir</span><span class="colon">:</span><span class="val">22 Juli 1995 <em>(Sabtu)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Waktu Lahir</span><span class="colon">:</span><span class="val">pukul 14:48 <em>(siang)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Kalender Lunar</span><span class="colon">:</span><span class="val">25 / bulan 6 / tahun Yi Hai <span class="hz">乙亥</span></span></div>',
     '<div class="row"><span class="lbl">Tanggal Lahir (Indonesia)</span><span class="colon">:</span><span class="val">30 Mei 1995 <em>(Selasa)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Tanggal Lahir (Tionghoa)</span><span class="colon">:</span><span class="val">tanggal 2 bulan 5 tahun <span class="hz">乙亥</span> <em>(Yi Hai · 1995)</em></span></div>\n'
     '        <div class="row"><span class="lbl">Waktu Lahir</span><span class="colon">:</span><span class="val">pukul 10:35 <em>(pagi · 巳時)</em></span></div>'),

    ('Penguasa Hari</span><span class="colon">:</span><span class="val">Kayu Pohon Besar <span class="hz">甲木</span></span>',
     'Penguasa Hari</span><span class="colon">:</span><span class="val">Logam Halus <span class="hz">辛金</span></span>'),
    ('Kayu &amp; Air <span class="hz">木 水</span>', 'Logam &amp; Air <span class="hz">金 水</span>'),

    # COVER metadata
    ('<span class="val">乙亥年 癸未月<span class="id">22 Juli 1995 · 14:48</span></span>',
     '<span class="val">乙亥年 辛巳月<span class="id">30 Mei 1995 · 10:35</span></span>'),
    ('<span class="val">甲木 · 傷官格<span class="id">Kayu Pohon Besar · Shang Guan Ge</span></span>',
     '<span class="val">辛金 · 正官格<span class="id">Logam Halus · Zheng Guan Ge</span></span>'),

    # Misc
    ('Michele · Profil', 'Lin Ru Yi · Profil'),
    ('— Michele', '— Lin Ru Yi'),
    ('subjek: Michele', 'subjek: Lin Ru Yi'),
    ('Subjek: Michele', 'Subjek: Lin Ru Yi'),
    ('>Michele<', '>Lin Ru Yi<'),

    # Day Master & Format global swap (longer first)
    ('傷官格', '正官格'),
    ('Shang Guan Ge', 'Zheng Guan Ge'),
    ('Pemikir Kreatif', 'Penjaga Disiplin'),
    ('Pencipta Kreatif', 'Penjaga Disiplin'),
    ('Kayu Pohon Besar', 'Logam Halus'),
    ('kayu pohon besar', 'logam halus'),
    ('Kayu Yang', 'Logam Yin'),
    ('甲木', '辛金'),
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

idx = DIR / "index.html"
if idx.exists():
    h = idx.read_text(encoding="utf-8")
    o = h
    for old, new in REPLACEMENTS:
        h = h.replace(old, new)
    if h != o:
        idx.write_text(h, encoding="utf-8")

print(f"\nUpdated identity in {count} files")
