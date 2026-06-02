# AUTORUN V4.5 — Production Playbook (FULL-MD MODE)

V4.5 = **PRODUCTION** (promoted dari sandbox2 ke v45/ pada 2026-05-02, refactor FULL-MD MODE pada 2026-05-07).

**FULL-MD MODE (2026-05-07):** Engine TIDAK compute apa-apa — semua data dari MD file. Web Claude / extraction agent baca foto → tulis MD → engine build → PDF. **Tidak ada lagi engine compute fallback** (sxtwl pillar, py-iztro, infer_relationship marriage, _compute_shensha, Ba Zhai gua formula, threshold DM strength, dll). Semua dihapus.

User boleh pilih versi: V3 (cache/), V4.3 (v43/), atau V4.5 (v45/) — semua produksi PDF ke `#result/{date}/`.

## Trigger
User kirim `{path foto} pakai V4.5` → langsung jalankan tanpa nanya.

## Flow (5 langkah ringkas)

### 1. Setup
- `subject_id` = nama folder lowercase (mis. `banzi2`)
- Foto di `<photos_dir>` (semua `.jpg/.jpeg/.png/.webp`)
- Output target: `#result/{today}/{Name}-{Hanzi}-{Birth}.pdf`

### 1.5 ~~MANDATORY — Pre-resize foto 768px~~ — **SKIPPED (Opsi A 2026-05-08)**

**Status**: di-skip mulai 2026-05-08. Folder `1_prepped/` upscale interpolation bikin hanzi kecil rapat blur (傷/偏, palace stars, sihua markers) → akurasi audit turun. User confirm visual check.

**Sekarang**: langsung pakai foto **original** di folder `<photos_dir>/` (atau sub-folder `{Nama}/` setelah Step 6 rename).

```powershell
# v45\prep_photos.py TIDAK dijalankan lagi sebagai default.
# Script masih ada — bisa dipakai manual kalau foto tertentu butuh rotate/contrast,
# tapi default workflow skip step ini.
```

Decision log: `v45/_AUDIT/DECISION_prep_photos_strategy.md` (Opsi A executed).

- Wall-clock saving: ~30-60 detik per render (skip prep step)
- Disk saving: ~50% (no duplicate `_prepped/` folder)
- Akurasi audit naik: hanzi pixel-sharp, no upscale artifact

**Rollback**: kalau foto tertentu bermasalah (miring/gelap), trigger manual `python v45\prep_photos.py "<photos_dir>"` untuk subject itu saja, lalu Read pakai `_prepped/` override.

### 2. OCR — PARALLEL BATCH READ (kunci speedup vs V4.3)

**V4.3 baseline**: Read 1 foto, parse, write, Read foto next, ulang 22-28×. Sequential = 4-6 menit.

**V4.5 cara**: kirim **multiple Read tool calls dalam SATU message** (Claude Code execute parallel).

- **Batch size: 10 foto per message DEFAULT** (sweet spot — empirik banzi2 7/msg = 3 min, 10/msg target ~2 min). Kalau Claude lapor "rate limit" → fallback ke 7/msg. Hanya turun ke <7 kalau benar2 error.
- Untuk tiap batch:
  1. Single message berisi N `Read` tool calls (full file path masing-masing) — Claude Code execute parallel
  2. Setelah hasil semua datang, ekstrak struktur per foto sekaligus, simpan dalam memori (jangan tulis per-foto ke file)
- Lanjut batch berikutnya sampai semua foto terbaca

**MANDATORY Step 2a — Cache hash sweep (skip foto yang sudah di-OCR):**

Sebelum batch Read pertama, **wajib** jalankan dengan **folder original** (Opsi A 2026-05-08):
```powershell
python v45\cache_check.py <photos_dir>
```
Output JSON: `{total, cached_count, needs_ocr_count, cached[], needs_ocr[]}`.

⚠️ **Catatan post-Opsi A**: cache hash sweep sekarang baca dari folder original (bukan `_prepped/`). Kalau ada cache lama dari prepped folder, hash beda → akan re-OCR. Itu OK (one-time hit).

- `cached[]` → load JSON dari `cache_file` masing-masing, **skip Read** (data sudah lengkap)
- `needs_ocr[]` → batch Read pakai `path` field di sini, lalu setelah ekstrak per foto, simpan via:
  ```powershell
  python v45\cache_save.py "<photo_path>" '<json_string>'
  ```
  (atau pipe stdin) — supaya next run cached.

Re-run subjek sama atau foto dengan SHA256 sama → cached_count = total → **OCR step instant 0 detik**.

**Apa yang diekstrak per foto** (FULL-MD MODE 2026-05-07):

**📖 Schema authoritative: `v45/WEB_CLAUDE_PROMPT.md`** — baca dulu, ikuti format `## DATA` + `## TAFSIR` + `## DATA_EXTRA` per template di sana.

Ringkas, schema FULL-MD ekstrak:
- **Identity**: name_id, name_hanzi, gender, lahir_tanggal (solar), lahir_jam
- **Pillars**: pilar_tahun/bulan/hari/jam (dari grid BaZi utama)
- **Wuxing per-stem**: xiantian_jia/yi/.../gui (10 stems, dari 先天體檢)
- **Wuxing total**: wuxing_jin/shui/mu/huo/tu (sum 2-stem per elemen)
- **Wangdu scores**: wangdu_jia_mu/.../gui_shui (10 stems) + wangdu_total_* (5 elemen, dari 批命備註)
- **DM strength**: dm_strength (旺/弱/平), dm_strength_label_id (Kuat/Lemah/Seimbang), dm_pos_score, dm_neg_score
- **Yong/Ji**: yong_shen, ji_shen (from 用神/忌神 layar — **JANGAN derive sendiri**)
- **Format**: format (from 八字論斷 / 卦格 — **JANGAN default ke 正官格**)
- **Da Yun**: da_yun (10 cycles), da_yun_arah (順行/逆行), da_yun_start_age
- **Marriage**: marriage_cocok, marriage_hindari (from layar **婚配** — **JANGAN derive 三合/六合**)
- **Yang Zhai**: yang_zhai_gua (1 hanzi gua, from layar 陽宅)
- **Zi Wei**: ziwei_ming_zhu, ziwei_shen_zhu, ziwei_ming_gong, ziwei_shen_gong, ziwei_wu_xing_ju, ziwei_shi_jun
- **Shen Sha**: shen_sha_list ("天乙貴人@日, 文昌@月, ..." dari layar 神煞)
- **Optional**: nayin_*, canggan_*

**`## DATA_EXTRA` arsip** (SKIP by parse_md.py, tapi WAJIB diisi kalau foto ada — future-proof): chou_shen, xi_shen, xian_shen, xiantian_organ_*, gushuyun, quan_ju, fumu_bazi, shiye, xing_qing, liu_nian_*, ziwei_stars_*, ti_xiang, shi_shen_per_pilar, chang_sheng_per_pilar, ming_gong_bazi, kong_wang, shen_sha_detail, industri_full, marriage_*_tafsir_*

Field tidak terbaca → **null** (BUKAN omit). Engine handle null = tampil "—" di PDF.

**Step 2b — Dedup semantik (token saver tambahan):**

WhatsApp screenshot user **sering ada duplikat** (foto layar yang sama, retake, screenshot beruntun). SHA256 cache cuma catch byte-identik, tapi konten serupa lolos.

Setelah hash sweep, sebelum batch Read, lakukan triage cepat:
- Lihat ukuran file di `needs_ocr[]`. Foto dengan size persis sama (±5%) **kemungkinan besar duplikat** → cukup Read 1, skip yang lain.
- Kalau foto-foto WhatsApp punya timestamp berurutan dalam 1-2 detik (lihat dari nama file `at HH.MM.SS` dan `(1)` `(2)` suffix) → kemungkinan retake → Read 1 yang paling besar (kualitas tertinggi), skip yang lain.
- HASIL OCR untuk foto yang di-skip: copy hasil dari foto "kembarnya" (cache_save pakai hash foto skip itu, isi sama).

Dedup ini opsional — kalau ragu, Read semua (lebih aman). Empirik: WhatsApp screenshot 28 foto biasanya bisa dedup ke 18-22 unik.

### 3. Tulis hasil ekstraksi → MD file (FULL-MD MODE)

Gabung semua foto → 1 MD file struktur `# Name` + `## DATA` + `## TAFSIR` + `## CATATAN` + `## DATA_EXTRA`. Tulis sekali ke:
```
v45/data/subjects/{subject_id}.md
```
Format MD: ikut template di `v45/WEB_CLAUDE_PROMPT.md`. Engine `parse_md.py` akan baca file ini saat build.

**JANGAN** tulis per-foto. **JANGAN** tulis raw text foto. **JANGAN** tulis ke `.ocr.json` langsung (engine generate `.ocr.json` otomatis dari MD saat build).

### 4. Build + Render PDF (WAJIB JALANKAN — JANGAN STOP DI STEP 3)

⚠️ **PENTING:** Step 4 ini WAJIB dilakukan. JANGAN stop setelah tulis MD file di Step 3 — pipeline belum selesai sampai PDF generated.

Jalankan command ini via Bash tool:
```powershell
cd c:\Users\sukam\OneDrive\Documents\Ramalan\v45
python build_pdf.py {subject_id}
```

`build_pdf.py` jalankan: `parse_md.py` (MD → ocr.json) → `build_from_ocr.py` (FULL-MD MODE: pull MD → subject.json, no compute) → `render.py` (Chrome → PDF). Field MD null → tampil "—" di PDF.

**Verify:** setelah command selesai, output terakhir harus tampilkan path PDF di `#result/{date}/`. Kalau tidak ada PDF path → ada error, debug + retry. JANGAN report success ke user kalau PDF belum ada.

**Common reason workflow stop di sini:**
- Context limit setelah heavy parallel batch Read 28 foto. Solusi: kalau context tinggal sedikit, prioritas absolute = run `python build_pdf.py {id}` walaupun report ke user pendek. PDF lebih penting daripada laporan detail.
- Kelupaan run command. Solusi: SEBELUM step 5 report, double-check file `#result/{today}/{name}-*.pdf` exists.

### 5. Report (HANYA SETELAH Step 4 selesai dengan PDF generated)

```
- PDF: #result/{date}/{Name}-{Hanzi}-{Birth}.pdf
- Size: X MB
- Total time: X menit Y detik
- Foto count: N
- Field missing/fallback (kalau ada)
```

### 6. Auto-rename foto folder (WAJIB setelah Step 5)

Setelah PDF success + report, RENAME foto folder dari numeric (1-10) ke nama subjek (Indonesian latin) supaya next time user buka folder bisa langsung tahu siapa subjeknya.

```powershell
cd c:\Users\sukam\OneDrive\Documents\Ramalan\v45
python rename_foto_folder.py "<foto_folder_path>" {subject_id}
```

Contoh:
```powershell
python rename_foto_folder.py "C:\...\foto\database\07-05-2026\1" lijialing
# Output: [OK] Renamed: '1' → 'Li Jia Ling' di ...\07-05-2026
```

**Behavior:**
- Read MD `data/subjects/{subject_id}.md` field `nama:` (mis. "Li Jia Ling", "Wu Huan Yang")
- Sanitize (remove special chars unsafe for Windows folder names)
- Rename folder
- IDEMPOTEN: skip kalau folder sudah bukan numeric (1-10) — aman re-run
- SKIP kalau target name folder sudah ada (no overwrite)

**Catatan:** prepped folder `{N}_prepped/` (kalau ada legacy) TIDAK ikut di-rename. Post-Opsi A (2026-05-08), prep step skipped → tidak ada folder `_prepped/` baru dibuat.

---

## Daily Folder Setup (Pre-workflow)

Sebelum mulai daily render, user setup folder hari ini + 10 sub-folder kosong via:

```powershell
cd c:\Users\sukam\OneDrive\Documents\Ramalan\v45
python daily_folder_setup.py
```

Output: `foto/database/{DD-MM-YYYY}/1/`, `2/`, ..., `10/` — semua kosong, idempoten.

User drop foto subjek ke salah satu folder `1-10`, trigger pakai V4.5, setelah selesai folder otomatis ke-rename ke nama subjek (Step 6).

**Disarankan:** setup Windows Task Scheduler untuk run script ini otomatis setiap pagi (mis. jam 6:00). Atau run manual sebelum daily render pertama hari itu.

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
| PDF naming | `{Name}-{Hanzi}-{Birth}.pdf` | `{Name}-{Hanzi}-{Birth}.pdf` (no suffix, V4.5 = production default) |
| Output folder | `#result/{date}/` | `#result/{date}/` (V4.5 promoted ke prod) |

## NEVER (FULL-MD MODE)

- **Compute BaZi rule sendiri** — JANGAN derive marriage dari day branch (六合/三合), JANGAN compute pilar via sxtwl, JANGAN auto-detect format dari 十神 distribution, JANGAN threshold ≥25% untuk DM strength. Semua dari foto.
- **Default value sendiri** — JANGAN tulis `format: 正官格` kalau foto tidak ada label format. Tulis null.
- **Skip null** — Field tidak terbaca → tulis `null` (BUKAN omit). Engine perlu null untuk render "—".
- **Interpretasi BaZi sendiri** untuk field DATA — yong_shen, ji_shen, format, marriage list HARUS dari foto eksplisit. (Tafsir prose di TAFSIR boleh "percantik" kalau foto ada source.)
- Modifikasi `v43/` (production V4.3 LOCKED)
- Modifikasi `cache/michele/`, `cache/linruyi/`, `cache/_shared/` (V3 LOCKED)
- Ubah design / template HTML / CSS / substitution rules (LAYOUT V4.5 FREEZE)
- Read foto 1-by-1 sequential (defeat the V4.5 purpose — pakai parallel batch 10/msg)

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
