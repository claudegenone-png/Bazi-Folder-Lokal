# AUTORUN V4.5 — Sandbox2 Playbook (Claude-side optimization)

V4.5 = sandbox testing untuk **speed + token efficiency** dari sisi Claude (IDE), bukan API SDK.
Production daily render TETAP V3 (cache/) atau V4.3 (v43/). **Sandbox2 jangan overwrite `#result/`**.

## Trigger
User kirim `{path foto} pakai V4.5` → langsung jalankan tanpa nanya.

## Flow (5 langkah ringkas)

### 1. Setup
- `subject_id` = nama folder lowercase (mis. `banzi2`)
- Foto di `<photos_dir>` (semua `.jpg/.jpeg/.png/.webp`)
- Output target: `sandbox2/_pdf_out/{today}/{Name}-{Hanzi}-{Birth}-V4.5.pdf`

### 1.5 MANDATORY — Pre-resize foto 768px (token saver ~60%)

```powershell
python sandbox2\prep_photos.py "<photos_dir>"
```
Output stdout: `<photos_dir>_prepped/` (folder sibling). Mulai langkah selanjutnya **pakai folder prepped ini** untuk Read.

- Idempoten: foto sudah pernah prep → skip (re-run instant).
- Saving: file size ~62%, Claude vision token ~60-65%.
- 768px masih fully legible untuk Hanzi screenshot Xing Qiao (verified banzi2).

### 2. OCR — PARALLEL BATCH READ (kunci speedup vs V4.3)

**V4.3 baseline**: Read 1 foto, parse, write, Read foto next, ulang 22-28×. Sequential = 4-6 menit.

**V4.5 cara**: kirim **multiple Read tool calls dalam SATU message** (Claude Code execute parallel).

- **Batch size: 10 foto per message DEFAULT** (sweet spot — empirik banzi2 7/msg = 3 min, 10/msg target ~2 min). Kalau Claude lapor "rate limit" → fallback ke 7/msg. Hanya turun ke <7 kalau benar2 error.
- Untuk tiap batch:
  1. Single message berisi N `Read` tool calls (full file path masing-masing) — Claude Code execute parallel
  2. Setelah hasil semua datang, ekstrak struktur per foto sekaligus, simpan dalam memori (jangan tulis per-foto ke file)
- Lanjut batch berikutnya sampai semua foto terbaca

**MANDATORY Step 2a — Cache hash sweep (skip foto yang sudah di-OCR):**

Sebelum batch Read pertama, **wajib** jalankan dengan PREPPED dir (langkah 1.5):
```powershell
python sandbox2\cache_check.py <photos_dir>_prepped
```
Output JSON: `{total, cached_count, needs_ocr_count, cached[], needs_ocr[]}`.

- `cached[]` → load JSON dari `cache_file` masing-masing, **skip Read** (data sudah lengkap)
- `needs_ocr[]` → batch Read pakai `path` field di sini, lalu setelah ekstrak per foto, simpan via:
  ```powershell
  python sandbox2\cache_save.py "<photo_path>" '<json_string>'
  ```
  (atau pipe stdin) — supaya next run cached.

Re-run subjek sama atau foto dengan SHA256 sama → cached_count = total → **OCR step instant 0 detik**.

**Apa yang diekstrak per foto** (skema sama V4.3 biar `build_from_ocr.py` jalan tanpa modif):
```
screen_type, tafsir_section, name_id, gender_hz, birth_solar, birth_lunar_text,
pillars{year{stem_hz,branch_hz}, month{...}, day{...}, hour{...}},
wuxing{jin,shui,mu,huo,tu}, yong_shen_hz, ji_shen_hz, format_hz,
da_yun[{age,stem_hz,branch_hz}], marriage{cocok_branches[],hindari_branches[]},
yang_zhai_gua_hz,
zi_wei{ming_zhu_hz, shen_zhu_hz, ming_gong_branch_hz, shen_gong_branch_hz, wu_xing_ju_hz, shi_jun_hz}
```
Field tidak terbaca → **omit** (jangan tulis null, jangan tebak).

**Step 2b — Dedup semantik (token saver tambahan):**

WhatsApp screenshot user **sering ada duplikat** (foto layar yang sama, retake, screenshot beruntun). SHA256 cache cuma catch byte-identik, tapi konten serupa lolos.

Setelah hash sweep, sebelum batch Read, lakukan triage cepat:
- Lihat ukuran file di `needs_ocr[]`. Foto dengan size persis sama (±5%) **kemungkinan besar duplikat** → cukup Read 1, skip yang lain.
- Kalau foto-foto WhatsApp punya timestamp berurutan dalam 1-2 detik (lihat dari nama file `at HH.MM.SS` dan `(1)` `(2)` suffix) → kemungkinan retake → Read 1 yang paling besar (kualitas tertinggi), skip yang lain.
- HASIL OCR untuk foto yang di-skip: copy hasil dari foto "kembarnya" (cache_save pakai hash foto skip itu, isi sama).

Dedup ini opsional — kalau ragu, Read semua (lebih aman). Empirik: WhatsApp screenshot 28 foto biasanya bisa dedup ke 18-22 unik.

### 3. Tulis hasil OCR (1× write saja)

Gabung semua foto → 1 dict merged (rule: first-non-empty wins per key, `da_yun` array dari foto pertama yang punya). Tulis sekali ke:
```
sandbox2/data/subjects/{subject_id}.ocr.json
```
**JANGAN** tulis per-foto, **JANGAN** tulis raw_text — boros token.

### 4. Build + Render PDF (1 command)

```powershell
cd c:\Users\sukam\OneDrive\Documents\Ramalan\sandbox2
python build_pdf.py {subject_id}
```

(Kalau identitas perlu manual override karena OCR gagal):
```
python build_pdf.py {subject_id} --name "Nama" --hanzi 漢字 --gender Pria --date 1995-07-22 --time 10:35
```

`build_pdf.py` jalankan: `build_from_ocr.py` → native pillars compute → `render.py` → Chrome → PDF.

### 5. Report

```
- PDF: sandbox2/_pdf_out/{date}/{Name}-{Hanzi}-{Birth}-V4.5.pdf
- Size: X MB
- Total time: X menit Y detik
- Foto count: N
- Field missing/fallback (kalau ada)
```

---

## Apa yang IDENTIK V4.3 (jangan diubah)

- HTML templates (24 file di `templates/`)
- CSS, font, asset SVG
- `build_from_ocr.py`, `build_subject.py`, `compute_pillars.py`, `lookups.py`, `render.py` substitution rules
- Output schema `{id}.ocr.json` dan `{id}.json`

→ PDF V4.5 wajib byte-identik V4.3 untuk subjek + foto sama.

## Apa yang BEDA V4.3 → V4.5

| Aspek | V4.3 daily | V4.5 daily |
|---|---|---|
| Read tool | sequential per foto | **parallel batch 5-8 foto/message** |
| ocr.json write | bisa per-foto | **1× write akhir** |
| Chrome budget | 8000ms | **2500ms** (sudah patched) |
| PDF naming | `{Name}-{Hanzi}-{Birth}.pdf` | `{Name}-{Hanzi}-{Birth}-V4.5.pdf` |
| Output folder | `#result/{date}/` | `sandbox2/_pdf_out/{date}/` |

## NEVER

- Modifikasi `v43/` (production V4.3 LOCKED)
- Modifikasi `cache/michele/`, `cache/linruyi/`, `cache/_shared/` (V3 LOCKED)
- Overwrite `#result/` (sandbox PDF wajib ke `sandbox2/_pdf_out/`)
- Ubah design / template HTML / CSS / substitution rules
- Tulis raw_text ke ocr.json (boros)
- Read foto 1-by-1 sequential (defeat the V4.5 purpose)

## Optional: API fallback (belum dipakai daily)

`engines/ocr.py` masih ada — pakai Anthropic SDK + parallel ThreadPool. Jalan kalau `ANTHROPIC_API_KEY` set:
```
python cli.py <photos_dir> <subject_id>
```
Tidak relevan untuk daily flow user (vision Read tool sudah gratis).

## Target benchmark (revised dari hasil banzi2 actual)

- V4.3 daily baseline: **~6-7 menit** (22-28 foto, sequential Read)
- V4.5 actual banzi2 (28 foto, batch 7/msg): **3 menit** ← saving 50%
- V4.5 target (batch 10/msg + cache hash): **~2 menit** untuk subjek baru, **<1 menit** untuk re-run cached subjek

## Lessons dari banzi2 (2026-05-02)

- Batch 7 foto/msg = ~30s/batch → 4 batch × 30s = 2 min OCR. Belum optimal.
- Render+PDF: 38s konsisten (Chrome 2500ms patched, sweet spot).
- **PDF gradient white-box bug** muncul di pseudo-element `::before` dengan `background: radial-gradient(...)`. Fix: split jadi `background-color: transparent` + `background-image: gradient(...)`. Sudah dipatch di `page_profile.html` + `page_17_palace1.html` (sandbox2 only — V4.3 production tidak disentuh). Kalau muncul lagi di pseudo lain, pakai pattern fix yang sama.
