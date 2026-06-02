# AUTORUN — Daily Generate Laporan Ramalan

## Trigger patterns

## Pattern A (V4.5): Foto Prep — siapkan untuk Web Claude

User kirim:
- **Path folder foto** (e.g., `C:\Users\sukam\OneDrive\Documents\Ramalan\foto\database\11-40`)
- **Versi** `v4.5`

Contoh:
```
C:\Users\sukam\OneDrive\Documents\Ramalan\foto\database\11-40
v4.5
```

**Auto flow Pattern A:**
1. Bikin folder kerja `{path}_prepped/` (atau di `v45/data/foto/{name}/`)
2. **Upscale + sharpen foto** (resolusi tinggi supaya Web Claude akurat baca Hanzi/angka)
3. Optional: dedup duplicate screenshots, denoise
4. Output: folder berisi foto-foto siap upload + STOP
5. **Kasih instruksi user**: "Upload semua foto di {path_prepped} ke Claude Web (claude.ai), paste isi `v45/WEB_CLAUDE_PROMPT.md`. Output Web Claude = MD. Save ke folder, lalu kirim trigger Pattern B."
6. **JANGAN auto-call Web Claude**, JANGAN coba OCR sendiri pakai Read tool. User punya control penuh ke Web Claude.

**Output expected user:** path file MD (untuk Pattern B berikutnya)

## Pattern B (V4.5): MD audit + build PDF
User kirim:
- **Path MD file** (e.g., `C:\Users\sukam\Downloads\Test\LinWenhan.md`)
- Kata kunci `v4.5` (di baris berikut atau di pesan terpisah)

Contoh:
```
C:\Users\sukam\Downloads\Test\LinWenhan.md
v4.5
```

**Auto flow Pattern B:**
1. Baca MD file lewat Read tool
2. **Audit otomatis**: verifikasi data fundamental
   - 4 pilar valid 60-甲子 cycle (polaritas yin/yang match)
   - Format (正印 vs 偏印 = polarity DM vs stem印)
   - Da Yun arah (陽男陰女順 / 陰男陽女逆) + sequence dari pilar bulan + valid combos + branch tidak skip
   - Marriage cocok/hindari sesuai 三合/六合/六沖/六害 dari day branch
   - Yang Zhai gua sesuai formula Ba Zhai
   - Tanggal lunar vs solar konsistensi
3. **Hasil audit:**
   - **Clean** → copy MD ke `v45/data/subjects/{id}.md` → run `python v45/build_pdf.py {id}` → kasih path PDF
   - **Ada error** → kasih prompt revisi untuk Web Claude (per memory `workflow_md_audit_loop.md` rule of thumb: full regen kalau impact >=3 section, patch kalau <3)
4. **JANGAN auto-fix MD** di VS Code, selalu balikan ke Web Claude untuk regenerate

Kamu (Claude) **langsung jalankan** sesuai versi tanpa nanya. Skip semua step verifikasi rutin.

---

## Aturan umum (semua versi)

- **V3**, **V4.3**, **V4.5** semua PRODUCTION. User boleh pilih flow mana saja.
- **OCR foto = pakai Read tool kamu sendiri** (gratis). Anthropic API SDK tidak diperlukan.
- **DILARANG** sentuh `cache/michele/`, `cache/linruyi/`, `cache/_shared/` (V3 LOCKED) tanpa permintaan eksplisit user.
- **DILARANG** sentuh `v43/templates/`, `v43/engines/` (V4.3 LOCKED) tanpa permintaan eksplisit user.
- **DILARANG** sentuh `v45/templates/`, `v45/engines/` (V4.5 LOCKED) tanpa permintaan eksplisit user.
- **Subject_id** = nama folder lowercase (e.g., `banzi1`).
- **Output folder**: `OneDrive/Documents/Ramalan/#result/{YYYY-MM-DD}/`.

### PDF naming per versi
| Versi | Filename PDF |
|---|---|
| V3 | `{Name}-{Hanzi}-{Birth}.pdf` (no suffix) |
| V4.3 | `{Name}-{Hanzi}-{Birth}-V4.3.pdf` |
| V4.5 | `{Name}-{Hanzi}-{Birth}.pdf` (no suffix — production default) |

V4.5 promoted ke production penuh → no suffix. Cuma V4.3 yang masih bersuffix (legacy/A-B compare).

---

## V3 (production manual flow)

**Lokasi:** `C:\Users\sukam\OneDrive\Documents\Ramalan\cache\{subject_id}\`
**Output:** `#result\{tanggal}\{Name}-{Hanzi}-{Birth}.pdf`

### Steps
1. Baca memory: `baseline_michele_v3.md`, `lessons_tommy_iteration.md`, `feedback_cover_dual_date.md`, `feedback_shared_templates.md`, `feedback_header_swap.md`
2. Buat folder `cache/{subject_id}/` copy dari `cache/michele/` (BUKAN trial Henry)
3. Pakai 6 shared templates dari `cache/_shared/` (TOC, intro, bab opener BaZi+Zi Wei, glossary, disclaimer)
4. OCR foto via Read tool — ekstrak: identity, 4 pilar, wuxing, format, yong/ji shen, da yun, marriage, yang zhai, zi wei, tafsir
5. Edit per-page sesuai data subjek (cover, profile, daymaster, marriage, dst)
6. Run `python build_pdf.py` di folder subjek (constants NAME_ID/NAME_HANZI/BIRTH di-set)
7. Output ke `#result/{today}/`

---

## V4.3 (production auto pipeline)

**Lokasi:** `C:\Users\sukam\OneDrive\Documents\Ramalan\v43\`
**Output:** `#result\{tanggal}\{Name}-{Hanzi}-{Birth}-V4.3.pdf`

### Steps
1. Baca `v43/AUTORUN.md` untuk playbook lengkap
2. OCR foto via Read tool — sequential (V4.3 design)
3. Tulis ke `v43/data/subjects/{subject_id}.ocr.json`
4. Run:
   ```
   cd v43
   python cli.py "<photos_dir>" <subject_id> --skip-ocr `
       --name "<Indo Name>" --hanzi "<漢字>" --gender Pria/Wanita `
       --date YYYY-MM-DD --time HH:MM
   ```

---

## V4.5 (production parallel + token saver — **DEFAULT recommendation**)

**Lokasi:** `C:\Users\sukam\OneDrive\Documents\Ramalan\v45\`
**Output:** `#result\{tanggal}\{Name}-{Hanzi}-{Birth}.pdf`

### Steps
1. Baca `v45/AUTORUN.md` untuk playbook lengkap (5 langkah: prep + cache + parallel batch Read + dedup + build_pdf)
2. **Wajib jalankan** dalam urutan:
   ```
   cd v45
   python prep_photos.py "<photos_dir>"     # → <dir>_prepped/, resize 768px
   python cache_check.py "<dir>_prepped"     # → JSON cached vs needs_ocr
   ```
3. Untuk `needs_ocr[]`: batch **10 foto per Read message** (parallel via Claude Code), hasil per foto → `python cache_save.py "<photo>" '<json>'`
4. Optional dedup semantik untuk WhatsApp screenshot serial
5. Merge → 1× write `v45/data/subjects/{subject_id}.ocr.json`
6. Run `python v45/build_pdf.py {subject_id} --name ... --hanzi ... --gender ... --date ... --time ...`

### Speed/token (vs V4.3 baseline ~6-7 min, ~42K vision tokens)
- Subjek baru: ~1.5-2 menit, ~14K vision tokens (saving ~70% / ~67%)
- Re-run subjek sama: ~40 detik (skip OCR sepenuhnya)

### Design/konten/akurasi
**MD-driven personalization (sejak Mei 2026).** Web Claude generate MD per subjek dari foto → engine inject ke template via TAFSIR anchors. Konten 60-70% berbeda per subjek (vs V4.3 yang token-swap saja). Master prompt: v45/WEB_CLAUDE_PROMPT.md.

### PDF render: Workflow B (image-based)
Sejak Mei 2026: HTML → Chrome --print-to-pdf (intermediate) → fitz/PyMuPDF rasterize @ 150 DPI → PIL pack image-only PDF. **Pixel-perfect identik di semua viewer** (mobile/laptop/WA/print). Eliminates cross-viewer rendering inconsistency. Trade-off: text tidak selectable, file ~4-5 MB. Deps: pymupdf + pillow (sudah terinstall).

### Input flow
- **MD-mode** (preferred): user kasih MD file → langsung . Skip OCR.
- **Photo-mode** (fallback): photo OCR pipeline lama (lihat steps 1-6 di atas).

---

## Report ke user (singkat)

- Link PDF + size
- Waktu total
- Versi yang dipakai
- Field yang missing/fallback (kalau ada — surface ke user)

---

## NEVER

- Tanya user soal step routine (auto mode)
- Nanya API key (pakai Read tool, gratis)
- Modifikasi V3 / V4.3 / V4.5 production templates/engines tanpa izin
- Tebak data kalau OCR partial — surface explicit
- Ubah design/konten template

---

## Kalau user kasih path SAJA tanpa versi

Default = **V4.5** (paling cepat + hemat token, design+konten identik V4.3). Kasih tahu user "default V4.5, kalau mau V4.3 atau V3 kasih `pakai V4.3` / `pakai V3`".


---

## V4.8 (MD-driven, sandbox testing)

**Trigger format:** user kirim path **MD file** (bukan foto) + `v4.8` / `V4.8`.

```
C:\Users\sukam\Downloads\laporan_xxx.md
v4.8
```

Atau satu baris:
```
C:\Users\sukam\Downloads\laporan_xxx.md v4.8
```

### Yang langsung dilakukan (tanpa nanya):

1. Verify file MD exists. Kalau tidak ada → kasih tahu user, stop.
2. Run:
   ```powershell
   cd "$env:USERPROFILE\OneDrive\Documents\Ramalan\sandbox_v48"
   python v48.py "<path-md>"
   ```
3. Output HTML otomatis tersimpan di:
   ```
   OneDrive\Documents\Ramalan\#result\{YYYY-MM-DD}\_test_v48\full_{Name}.html
   ```
4. Report ke user:
   - Path HTML output (clickable)
   - Jumlah halaman
   - Section count + UNKNOWN topics (kalau ada — dari extraction report)
   - Kalau extraction error → surface tanpa retry

### Aturan V4.8

- **Input = MD file**, BUKAN foto. Kalau user kasih folder foto + `v4.8` → kasih tahu V4.8 hanya terima MD, tolak.
- **Output = HTML** (PDF export V4.8 belum di-wire).
- **DILARANG** modifikasi `sandbox_v48/templates/` atau `sandbox_v48/extractors/` saat autorun. Itu mode editing terpisah.
- Multi-file: kalau user kasih beberapa MD path → render satu per satu, list semua HTML output.
- Kalau Python error import → kemungkinan OneDrive belum selesai sync. Tunggu 30 detik dan retry sekali; kalau masih error, surface ke user.

### Speed/token

- ~5-15 detik per MD (pure stdlib, no LLM call dalam pipeline V4.8).
- Tidak ada vision token cost (extractor murni regex).

