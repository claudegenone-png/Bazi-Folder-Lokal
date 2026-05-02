"""Round 3 — final English sweep."""
from pathlib import Path

DIR = Path(r"C:\temp\tommy")

REPLACEMENTS = [
    # Waktuline broken — should be "Lini Masa" or "Garis Waktu"
    ('Waktuline', 'Lini Masa'),
    ('Garis Hidup Lini Masa', 'Garis Hidup'),
    ('Garis Hidup · Lini Masa', 'Garis Hidup'),

    # Compatibility / Personality glosses
    ('· Compatibility', '· Kompatibilitas'),
    ('· Personality', '· Kepribadian'),
    ('Compatibility · 婚配', 'Kompatibilitas · 婚配'),
    ('Compatibility', 'Kompatibilitas'),
    ('Personality', 'Kepribadian'),

    # Day Yun / Decade Cycles
    ('· Decade Cycles', '· Siklus 10 Tahunan'),
    ('Decade Cycles', 'Siklus 10 Tahunan'),

    # Stems & Branches
    ('10 Heavenly Stems', '10 Batang Langit (Tian Gan)'),
    ('12 Earthly Branches', '12 Cabang Bumi (Di Zhi)'),
    ('Heavenly Stems', 'Batang Langit'),
    ('Earthly Branches', 'Cabang Bumi'),

    # Section comments (HTML comments not visible but cleaning)
    ('<!-- Section 1:', '<!-- Bagian 1:'),
    ('<!-- Section 2:', '<!-- Bagian 2:'),
    ('<!-- Section 3:', '<!-- Bagian 3:'),
    ('<!-- Section 4:', '<!-- Bagian 4:'),
    ('<!-- Section 5:', '<!-- Bagian 5:'),

    # Synthesis page mantra label
    ('Mantra · 您 的 箴 言', 'Mantra · 您 的 箴 言'),  # keep

    # Misc remaining
    ('Total Rezeki', 'Jumlah Rezeki'),
    ('Total Wu Xing', 'Jumlah Wu Xing'),
    ('Total ', 'Total '),  # keep "Total" since it's also used in Indonesian

    # Cover specifically
    ('Versi V3 · Mei 2026', 'Mei 2026'),

    # Page 14 specific - "Da Yun Waktuline" comment
    ('Da Yun Waktuline', 'Da Yun Lini Masa'),
    ('PAGE-SPECIFIC: Da Yun', 'PAGE-SPECIFIC: Da Yun'),  # keep CSS comment

    # Da Yun timeline title
    ('Garis Hidup · Lini Masa 10 Tahunan', 'Garis Hidup · 10 Tahunan'),

    # 大運 timeline 10 tahunan (already in Indo, just clean up)
    ('Lini Masa 10 Tahunan', '10 Tahunan'),

    # If there's "Foundation"
    ('Foundation', 'Dasar'),

    # Card / Section common labels
    ('>Section<', '>Bagian<'),
    ('>Card<', '>Kartu<'),

    # Group
    ('Group', 'Kelompok'),

    # Quote
    ('· Quote', '· Petikan'),
    ('Quote', 'Petikan'),

    # Profile (English) — but Profil is Indonesian. Skip if standalone.

    # Common short words in body
    ('More info', 'Info Lebih Lanjut'),
    ('Read more', 'Baca lebih'),

    # Remove redundant English in comments inside SVG/HTML where harmless
    ('<!-- Background rings -->', '<!-- Lingkaran latar -->'),
    ('<!-- 8 direction badges -->', '<!-- 8 badge arah -->'),
    ('<!-- 12 Shio badges -->', '<!-- 12 badge shio -->'),
    ('<!-- Center marker -->', '<!-- Pusat -->'),
    ('<!-- Compass cross -->', '<!-- Salib kompas -->'),
    ('<!-- Outer ornament -->', '<!-- Ornamen luar -->'),
    ('<!-- Cardinal axis lines -->', '<!-- Garis sumbu utama -->'),

    # Glossary "Doorway" already done? Re-check
    ('Mén · Doorway', 'Mén · Pintu'),
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
