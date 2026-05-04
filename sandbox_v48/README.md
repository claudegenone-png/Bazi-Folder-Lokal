# Sandbox V4.8 — Universal Pretty PDF (Tionghoa Astrology Report)

V4.8 generates beautiful PDF reports from Markdown source files containing
Chinese astrology data (BaZi, Zi Wei Dou Shu, Feng Shui, etc).

## Architecture

3-layer pipeline:

1. **Extractors** (`extractors/`) — parse MD into canonical data model
2. **Canonical Model** (`canonical_model.py`) — fixed schema, all fields optional
3. **Templates** (`templates/`) — render HTML with inline CSS

## Quick Start

`powershell
# Render MD to HTML
python v48.py "path/to/laporan.md"
# → outputs to: %USERPROFILE%/OneDrive/Documents/Ramalan/#result/{date}/_test_v48/full_{Name}.html

# Convert HTML to PDF (Chrome headless)
.\export_pdf.ps1 "<html_path>" "<Name>" "<Hanzi>" "<Birth>"
# → outputs to: #result/{date}/{Name-Dashed}-{Hanzi}-{Birth}.pdf
`

## Requirements

- Python 3.10+ (no external packages needed — pure stdlib)
- Google Chrome or Microsoft Edge (for PDF export)

## Pages Generated

1. Cover (with shio + Day Master + birth info)
2. Daftar Isi (TOC)
3. Pengantar & Cara Membaca
4. Empat Pilar BaZi (4 pillars + Wu Xing chart)
5. Karakter & Kepribadian
6. Peta Bintang Zi Wei
7. Detail 12 Istana Hidup
8. Feng Shui Rumah
9. Aspek Kehidupan (Karir, Keuangan, Pernikahan, Kesehatan, dll — generic adaptive)
10. Bintang Khusus (神煞)
11. Tabel Nasib Tahunan (Da Yun + Liu Nian)
12. Takdir & Misi Hidup (宿命)
13. Ramalan Tahunan (per-year)
14. Hikmat Klasik (古書云)
15. Kesimpulan & Saran
16-17. Daftar Istilah (Glossary)
18. Disclaimer & Etika

## Adaptive Extraction

Extractors handle 3+ MD format variants. Sections/topics that aren't
recognized are rendered via generic_section.py with auto-detected layout.

## Naming Convention

Output PDFs follow V4.5 naming: `{Name}-{Hanzi}-{Birth}.pdf` (no version suffix).
