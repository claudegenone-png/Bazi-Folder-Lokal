# AUTORUN — Daily Generate Laporan Ramalan

User akan kirim 2 input pendek:
- **Path folder foto** (e.g., `C:\Users\sukam\Downloads\banzi1`)
- **Versi** yang dipakai (`V3`, `V4.3`, atau `V4.5`)

Contoh prompt user:
```
C:\Users\sukam\Downloads\banzi1 pakai V4.5
```

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
**100% identik V4.3** — template + render engine verbatim copy v43/, +2 patch CSS (gradient white-box fix di pseudo). PDF visual identik.

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
