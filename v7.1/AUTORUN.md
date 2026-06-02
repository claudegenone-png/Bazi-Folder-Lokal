# AUTORUN V7.1 — Production Playbook (V7 + Halaman Kesehatan + Triple-Vote + Crop Pipeline)

V7.1 = V7 fork production-ready (2026-05-09) dengan tambahan **halaman Kesehatan** (sisip sebelum Informasi Tambahan = page 16, total 27 pages) + **triple-vote audit gate** + **crop preprocessing pipeline** (2026-05-10) untuk 100% akurasi 19 high-risk fields panel kiri foto BaZi grid.

## ⚠ MODEL POLICY (2026-05-31) — SONNET ONLY, NO OPUS
Daily render V7.1 **WAJIB Sonnet**, jangan Opus (hemat token, Sonnet cukup untuk OCR+translate+rakit).
- Main loop: jalankan `/model sonnet` sebelum render (atau tambah `"model": "sonnet"` di `~/.claude/settings.json` secara manual — edit otomatis oleh Claude ke-block classifier karena file berisi permissions list).
- SEMUA subagent (translator, audit, dll) WAJIB pakai `model: "sonnet"` di Agent tool. Jangan biarkan inherit Opus.
- Berlaku untuk V7.1 normal MAUPUN `pakai V7.1 fast` (lihat `AUTORUN_FAST.md`).

V7.1 inherit semua fitur V7 (FULL-MD MODE + V4.9 audit gate + 9-step pipeline). Beda dari V7:
1. Tambah halaman Kesehatan (Block A: 10-organ energy map dari 先天體檢 + Block B: 疾厄 palace narrative dari ZiWei).
2. **Triple-vote** untuk xiantian_* (10) + 5-elemen (5) + canggan_* (4) — autonomous, no human verify.
3. **Crop preprocessing pipeline** (NEW 2026-05-10) — pre-crop 3 panel + enhance + 2x upscale sebelum spawn agen → eliminate attention dilution → akurasi naik 96% → 100% (test 6 foto, 113/114 cocok GT, 1 error karena foto 80% blur).

V7 (parallel folder, 26 pages tanpa Kesehatan + tanpa triple-vote) tetap available — user bebas pilih.


## ⚠ ATURAN WAJIB — 12 ISTANA LENGKAP + ENHANCE LAYAR BURAM (2026-05-21)

**Akar masalah subjek CS (2026-05-21):** narasi 12 istana ditulis RINGKAS (bukan terjemah penuh), dan layar buram (命宮, 官祿) tidak di-enhance dulu sebelum tulis MD. Tidak ketahuan sampai user komplain. Cegah selamanya dengan aturan ini:

1. **12 istana = terjemah PENUH & faithful, JANGAN diringkas.** Tiap layar 詳細解說 (命宮/兄弟/夫妻/子女/財帛/疾厄/遷移/僕役/官祿/田宅/福德/父母) WAJIB diterjemahkan **lengkap** ke `palace_*_insight` (semua kalimat foto, termasuk klausa kondisional "如與X同宮"). Bukan cuma 命宫 (yang sudah wajib) — SEMUA 12.
2. **Layar narasi buram WAJIB di-enhance dulu** sebelum tulis MD: crop region teks + `ImageEnhance.Contrast(1.4-1.6)` + `Sharpness(2.0-2.5)` + upscale 2-3x LANCZOS, lalu Read ulang. (Lihat pola di `_AUDIT_LOGS/crops_{id}/*_enh.jpg`.) Jangan tulis MD dari layar yang masih buram.
   - **Script otomatis (NEW 2026-05-24):** `python v7.1/narrative_crop.py <foto_or_folder> <output_dir>` — apply PIL Contrast 1.5 + Sharpness 2.2 + 2x LANCZOS upscale. Default params sudah di-tune untuk WhatsApp screenshot CRT layar.
   - Saran workflow: di Step 0.6 (atau sebelum Read foto palace), enhance dulu folder foto ke `_AUDIT_LOGS/enh_{subject_id}/`, lalu Read enhanced version.
3. **Karier (官祿) & Rezeki (財帛)** termasuk yang sering panjang & padat — pastikan penuh (cara cari uang, peringatan bintang, kelemahan, profesi spesifik).
4. **preflight.py sekarang punya `check_palace_completeness`**: warning otomatis kalau ada insight istana < 220 char (dicurigai diringkas) atau < 12 istana terisi. Kalau muncul warning ini saat daily render → baca ulang foto istana itu, terjemah penuh, jangan lanjut build.
5. **RULE 7 di WEB_CLAUDE_PROMPT.md (NEW 2026-05-24)** — strict source binding palace→foto + klausa count ≥80% + verbatim translate Hanzi nuanced. Anti-halusinasi BPA-style (Zinu pakai foto salah, Puyi drop paragraf, Fumu mistranslate). Wajib comply saat tulis insight.


## ⚠ ATURAN ANTI-HARDCODE BLEED (2026-05-29)

**Akar masalah subjek AVH (2026-05-29):** 2 halaman (`page_xingqing_full.html` 性情 & `page_overview.html` 全局總論) dipromote 2026-05-25 dengan **konten sampel statis (Leonardo)** tanpa wiring substitusi → SEMUA daily render sejak itu menampilkan data Leonardo di 2 halaman tsb (nama, shio, 戊土, prosa). Tidak ketahuan sampai user cek manual. Cegah selamanya:

1. **DILARANG konten per-subjek statis di template.** Semua data subjek (nama, shio, DM, pilar, prosa istana/性情/全局, arah, dll) WAJIB lewat `{{PLACEHOLDER}}` atau `<!-- TAFSIR:slug -->...<!-- /TAFSIR -->`. Template baru/promosi TIDAK boleh punya nama/angka/prosa subjek tertanam. Konten sampel hanya boleh di komentar `<!-- ... -->`.
2. **Saat promote sandbox → production:** WAJIB render **2 subjek BERBEDA** lalu diff halaman. Kalau ada teks identik di field yang seharusnya beda (nama/prosa/arah) → itu hardcode bleed, perbaiki dulu sebelum promote.
3. **Guard otomatis:** `preflight.py --post-render` sekarang punya cek **BLEED** (scan nama sampel: Leonardo/莊小敏/Tanah Gunung/戌 Anjing) + cek **ZONE?** (kartu zona hanzi "?"). Kalau muncul saat daily render → ada bleed/label tak ke-map, JANGAN kirim PDF, perbaiki dulu.
4. **`build_pdf.py` auto-hapus `__pycache__`** (OneDrive bikin .pyc basi → edit engine tak kebaca). Jangan revert ini.
5. Field 性情 → MD section `### Kepribadian Detail` (`poin:` list). Field 全局總論 → `### Sekilas Hidup` (`card:` list "Label | teks"). Keduanya foto-strict, faithful, no halusinasi.

## Trigger
- User kirim `{path foto} pakai V7.1` → jalankan workflow V7.1 (27 pages + triple-vote).
- User kirim `{path foto} pakai V7` → fall back V7 (26 pages baseline, no triple-vote).

## 🚀 PROMOTION 2026-05-25 — PDF v3 (37 pages baseline)

Sandbox v7.2_sandbox_pdfv3 promoted ke production V7.1. Perubahan:

### Templates baru (sisip di Bagian I setelah Day Master)
- `page_xingqing_full.html` — Kepribadian Detail (sumber 性情, 5 paragraf bernumber, auto-shrink font default 9pt)
- `page_overview.html` — Sekilas Hidup (sumber 全局總論, 5 mini-card pasangan/anak/harta/ayah/istri)

### Templates patched
- `page_palace_caibo.html` — Caifu combined: BaZi 財富 (正財/偏財) + ZiWei 財帛宮 dalam 1 page
- `page_20_kesimpulan.html` — Default font 11pt→9.5pt + line-height 1.4 (proactive shrink)
- `page_02_toc.html` — Bagian IV "Lampiran" 1-bar combined (Glossary + Disclaimer)
- `page_22_glossary.html` — Footer/h-num = Roman IV
- `page_23_disclaimer.html` — Footer/h-num = Roman V

### Engine patched
- `render.py` PAGE_ORDER → +2 entries (page_xingqing_full + page_overview) setelah page_06_daymaster
- `render.py` smart Kesimpulan split: kalau page 2 < 35% total content → keep 1 page + shrink

### Memory rules (lihat .claude/projects/.../memory/)
- `feedback_translation_full_detail_no_hallucination.md` — HARD RULE 1: NO source attribution dalam prose, HARD RULE 2: hanzi wajib translate inline (user tidak baca Hanzi)
- `feedback_rename_photos_sequential_step0.md` — Step 0 wajib daily render: rename foto sequential 1..N
- `feedback_analysis_framework.md` — Trigger "Jalankan analisis" = comprehensive mode (vertical+lateral)

### Backups
Semua file v7.1 yang ditimpa di-backup dengan suffix `.bak_promote_2026-05-25_1443`. Rollback dengan copy `.bak` kembali ke nama asli.

### Workflow upgrade
Daily render V7.1 ke depannya: faithful translator agent → main rakit profesional (12 palace + Kesimpulan + Sintesis). Hanzi inline translate wajib. No source attribution.


## STEP 0 — WAJIB: Rename foto sequential 1..N (NEW 2026-05-25)

**SEBELUM** apa-apa (sebelum cache_check, sebelum crop_panels, sebelum spawn audit agen), jalankan rename foto ke nomor sequential supaya user bisa easily reference per nomor di diskusi.

```powershell
cd c:/Users/sukam/OneDrive/Documents/Ramalan/v7.1
python rename_photos_sequential.py "<photos_dir>"
```

Output: `1.jpeg`, `2.jpeg`, ..., `N.jpeg` (preserve extension). Idempoten — kalau sudah sequential, skip no-op. cache_check.py pakai SHA256 content hash, jadi rename tidak invalidate cache. Wajib untuk V7.1, V7, V4.9, V4.5, V8, V9 (semua engine).

Detail rule: lihat memory `feedback_rename_photos_sequential_step0.md`.

## Triple-Vote Audit Gate (NEW 2026-05-09)

Untuk 19 field panel kiri BaZi grid yang rentan misread (xiantian per-stem, 5-elemen 用神/喜神/閒神/仇神/忌神, canggan per pilar), V7.1 spawn **2 subagent paralel di awal** (audit-blind + BaZi-specialist) → Python `audit_decide.py` voting per field. Kalau ambigu di Tier 1, auto-escalate ke **Tier 2** (spawn 2 BaZi-specialist baru) → re-vote dengan 5 reading. Tier 2 masih ambigu → STOP, lapor user retake foto.

Detail prompt: `v7.1/AUDIT_BAZI_PROMPT.md` (Tier 1) + `v7.1/AUDIT_BAZI_TIER2_PROMPT.md` (Tier 2).
Decision script: `v7.1/audit_decide.py` (deterministik Python, smoke test 15/15 PASS).

### Step 0.4 — Pre-crop foto BaZi grid (NEW 2026-05-10)

**Sebelum spawn Tier 1**, identifikasi foto BaZi grid utama dan jalankan:

```powershell
cd c:\Users\sukam\OneDrive\Documents\Ramalan\v7.1
python crop_panels.py "<foto_bazi_grid>" "_AUDIT_LOGS/crops_{subject_id}"
```

Output 3 file di `_AUDIT_LOGS/crops_{subject_id}/`:
- `{stem}__xiantian.jpg` — panel 先天體檢 (tight crop + enhance + 2x upscale)
- `{stem}__xiyong.jpg` — panel 喜用神
- `{stem}__bazi.jpg` — panel 八字 grid + 人元 row

Plus folder `{stem}__rows/` (10 row crops opsional). Estimasi: ~0.7 detik per foto.

**Why crop:** Multimodal attention dilution di foto utuh (1.5MB, multi-panel) bikin agen miss small cyan-on-blue digit. Tight crop + enhance + upscale → glyph relatif 3-5x lebih besar → akurasi 96% → 100%.

### Step 0.5 — Spawn 2 audit subagent paralel (T=0)

Bersamaan dengan first batch Read main agent:

```python
# Audit-blind (existing) — full 25 foto, all fields
Agent(
  description="Audit-blind extract V7.1",
  subagent_type="general-purpose",
  prompt=open("v49/BLIND_EXTRACT_PROMPT.md").read().format(
    subject_id=...,
    photos_dir=...,
    output_path="v7.1/_AUDIT_LOGS/{id}_blind.json"
  ),
  run_in_background=True
)

# BaZi-specialist Tier 1 (NEW 2026-05-10: 3 slots, baca CROPPED panels)
for slot in ("A", "B", "C"):
    Agent(
      description=f"BaZi-specialist Tier 1 V7.1 slot {slot}",
      subagent_type="general-purpose",
      prompt=open("v7.1/AUDIT_BAZI_PROMPT.md").read().format(
        subject_id=...,
        crops_dir=f"v7.1/_AUDIT_LOGS/crops_{subject_id}",
        full_foto_path=...,  # fallback kalau crop ada bagian terpotong
        audit_logs_dir="v7.1/_AUDIT_LOGS",
        slot=slot
      ),
      run_in_background=True
    )
```

3 slot baca SAMA 3 cropped panels — agreement strong = high confidence, disagreement = STOP atau Tier 2.

### Step 3.7 — Run audit_decide.py Tier 1

Setelah main MD ditulis (Step 3) dan ketiga BaZi-specialist subagent selesai, run:

```powershell
cd c:\Users\sukam\OneDrive\Documents\Ramalan\v7.1
PYTHONIOENCODING=utf-8 python audit_decide.py --test {subject_id} \
  _AUDIT_LOGS/test_{subject_id}_v7_agent_A.json \
  _AUDIT_LOGS/test_{subject_id}_v7_agent_B.json \
  _AUDIT_LOGS/test_{subject_id}_v7_agent_C.json
```

Decision logic (sudah encoded di `audit_decide.py`):
- Schema aliases lengkap: `canggan_year/year_canggan/renyuan_*`, `xiyong_5elem` packed string, pinyin/english → hanzi (mu/jin/wood/metal), conf/confidence dual key, numeric conf 0-1 → label
- Unanimity rule: 3/3 agree min med → PASS (lebih kuat dari per-cell conf)
- 5-shen unique constraint: auto-derive missing element kalau 4 PASS unik + 1 STOP, demote duplicate ke STOP

Exit 0 → semua 19 field PASS → update MD dengan decided values (override jika beda) → lanjut Step 4 build.
Exit 1 → ada STOP field → lanjut Step 3.8 (Tier 2 escalation auto-trigger).

### Step 3.8 — Tier 2 escalation (auto-trigger kalau Tier 1 STOP)

Untuk SETIAP STOP field di Tier 1, spawn 2 BaZi-specialist Tier 2 (slot D + E) paralel dengan **focused prompt** + **full foto fallback**:

```python
for slot in ("D", "E"):
    Agent(
      description=f"BaZi-specialist Tier 2 slot {slot}",
      subagent_type="general-purpose",
      prompt=open("v7.1/AUDIT_BAZI_TIER2_PROMPT.md").read().format(
        subject_id=...,
        crops_dir=f"v7.1/_AUDIT_LOGS/crops_{subject_id}",
        full_foto_path=...,  # WAJIB — Tier 2 boleh akses foto utuh
        stop_fields_list=...,        # dari Tier 1 _decision.json
        tier1_audit_trail_per_field=..., # untuk konteks "X agen baca Y"
        audit_logs_dir="v7.1/_AUDIT_LOGS",
        slot=slot
      ),
      run_in_background=True
    )
```

Tunggu kedua selesai → re-run audit_decide.py dengan 5 sources (A+B+C+D+E):

```powershell
PYTHONIOENCODING=utf-8 python audit_decide.py --test {subject_id}_t2 \
  _AUDIT_LOGS/test_{subject_id}_v7_agent_A.json \
  _AUDIT_LOGS/test_{subject_id}_v7_agent_B.json \
  _AUDIT_LOGS/test_{subject_id}_v7_agent_C.json \
  _AUDIT_LOGS/test_{subject_id}_v7_agent_D.json \
  _AUDIT_LOGS/test_{subject_id}_v7_agent_E.json
```

Exit 0 → semua field PASS dengan 5 reading → update MD → lanjut Step 4.
Exit 1 → masih STOP → lapor user dengan tabel reading per field + saran retake foto + STOP build.

**Test result 2026-05-10**: 6/6 foto baru, 113/114 fields cocok GT (99.1%). 1 error karena foto 80% blur (acceptable). 4/6 fotos perfect Tier 1 first-try, 2/6 needed Tier 2 escalation.

## Marriage page triple-vote (NEW 2026-05-15) — Step 0.5b + 3.7d

Halaman shio/marriage (`page_marriage.html`) **paling sering misread** karena foto 婚配 punya 2-4 tier compact dengan multiple shio list per tier. Triple-vote khusus untuk panel ini.

### Step 0.5b — Spawn 3 marriage-specialist subagent (WAJIB, paralel dengan Tier 1 BaZi)

Bersamaan dengan spawn 3 BaZi-specialist (Step 0.5), spawn 3 marriage agent:

```python
foto_marriage = "<path foto 婚配 — biasanya 1 foto specific>"
for slot in ("A", "B", "C"):
    Agent(
      description=f"Marriage triple-vote slot {slot}",
      subagent_type="general-purpose",
      prompt=open("v7.1/AUDIT_MARRIAGE_PROMPT.md").read().format(
        photo_path=foto_marriage,
        subject_id=subject_id,
        slot=slot,
        audit_logs_dir="v7.1/_AUDIT_LOGS"
      ),
      run_in_background=True
    )
```

Tunggu ke-3 agen selesai sebelum tulis MD field `marriage_*`.

### Step 3.7d — Run audit_marriage_decide.py

```powershell
cd c:\Users\sukam\OneDrive\Documents\Ramalan\v7.1
PYTHONIOENCODING=utf-8 python audit_marriage_decide.py {subject_id} \
  _AUDIT_LOGS/marriage_{subject_id}_A.json \
  _AUDIT_LOGS/marriage_{subject_id}_B.json \
  _AUDIT_LOGS/marriage_{subject_id}_C.json
```

Exit 0 (UNANIMOUS/MAJORITY) → use recommended MD field values dari output
Exit 2 (ESCALATE) → spawn 2 Tier 2 agen (slot D+E) → re-decide dengan 5 sources
Exit 3 (STOP) → user retake foto 婚配

Output decide script otomatis print recommended MD value:
```
marriage_cocok: 子, 巳, 酉
marriage_hindari: 辰, 午, 未, 戌
marriage_cocok_relationships: 子:大吉, 巳:大吉, 酉:大吉
```

Salin nilai ini ke MD `data/subjects/{id}.md` di section DATA.

### Step 3.7e — Semantic check (NEW 2026-05-15)

Setelah MD ditulis dan SEBELUM `python build_pdf.py`, spawn 1 verifier untuk catch translation flip / star name confusion / internal conflict:

```python
Agent(
  description=f"Semantic verifier V7.1 {subject_id}",
  subagent_type="general-purpose",
  prompt=open("v7.1/AUDIT_SEMANTIC_PROMPT.md").read().format(
    photo_dir=photos_dir,
    md_path=f"v7.1/data/subjects/{subject_id}.md",
    audit_logs_dir="v7.1/_AUDIT_LOGS"
  )
)
```

Output: `_AUDIT_LOGS/semantic_{subject_id}.json` dengan verdict per field.

Setelah verifier selesai, run decide:

```powershell
python audit_semantic_decide.py {subject_id}
```

Exit code:
- 0 = PROCEED ke build
- 2 = BLOCK (ada high-severity MISMATCH) — fix MD dulu (mis. star name salah, marriage shio salah, negation flipped)
- 3 = MANUAL_REVIEW — user keputusan

Field yang di-check (high-impact):
- `palace_fumu_insight` (sering negation flip)
- `palace_ming_gong_insight` (star name confusion)
- `ziwei_ming_gong` (天日 vs 天同 etc)
- `format` + `yong_shen` + `ji_shen` (exact label match)
- `marriage_*_tafsir` (semantic match cocok/hindari prose)
- `kesimpulan_narrative` (cross-check dengan DATA fields)

---

## Preflight validator (NEW 2026-05-15) — Step 3.9

**Auto-invoked by build_pdf.py at Step 0.5** (after MD parse, before subject build).

### Manual run
```powershell
cd c:\Users\sukam\OneDrive\Documents\Ramalan\v7.1
python preflight.py {subject_id}              # pre-build (validate MD)
python preflight.py {subject_id} --post-render # post-build (scan rendered HTML for ** leak)
```

### Checks performed
1. **Marriage shape** — cocok/hindari are valid 12 branches, no overlap, count consistent dengan tier labels
2. **5-elemen sum** — wuxing_jin+shui+mu+huo+tu total 7-9 (BaZi 4-pillar)
3. **shio_hz vs year_branch** — harus konsisten
4. **Critical fields** — `ming_gong` palace insight WAJIB ada (V7.1 page 16 paling penting)
5. **HTML ** leak (post-render only)** — scan `_build/{id}/*.html` untuk `**` literal yang escape `_md_inline()` — kalau ada, ada bug wiring di `render.py` (field injection lupa `_md_inline()` wrapper)

### Exit codes
- `0` = pass (build proceeds)
- `1` = warnings (build proceeds, warnings printed)
- `2` = hard fail (build ABORTS dengan pesan error jelas)

Hard fail conditions:
- `palace_ming_gong_insight` missing
- `marriage_cocok`/`marriage_hindari` contain invalid branches
- cocok ∩ hindari overlap

### Why preflight ada
Workaround errors yang sering muncul di session render:
- MD agen lupa ekstrak ming_gong prose → page 16 kosong → STOP early
- Shio hanzi (鼠/牛) salah ditulis sebagai branch (子/丑) → diketahui sebelum build
- ** literal markdown yang tidak ke-render karena field injection lupa md_inline wrapper

---

## Halaman Kesehatan (NEW)
- Source: foto BaZi grid kolom 先天體檢 (10 stem-organ count) + foto 疾厄 palace narrative (ZiWei)
- Auto-skip kalau xiantian + jie_e SEMUA null → page collapsed, total 26 pages (sama V7)
- Field MD baru:
  - `xiantian_*` (10 stems) — sudah ada di V7 schema, reuse
  - `jie_e_palace_hz` — verbatim hanzi narrative dari foto 疾厄
  - `jie_e_palace_id` — Indo translation (bullet list, 1 kalimat per bullet)
  - `jie_e_organ_focus_id` — kalimat utama "主的是須留心XX"

## Audit Gate WAJIB (sama V4.9)

V7 inherit audit gate dari V4.9 — bukan optional. Flow paralel:

```
T=0 ┬─► [MAIN] cache_check + parallel batch Read 37 foto + tulis MD ke v7.1/data/subjects/{id}.md
    │
    └─► [AUDIT-BLIND subagent] (background, paralel)
         baca foto blind → v7.1/_AUDIT_LOGS/{id}_blind.json
T → COMPARE (main) → verdict
    ├─ PASS / FAIL_FIXABLE ≤5 → build PDF
    ├─ FAIL_AMBIGUOUS → escalate AUDIT-2 + DECIDER
    ├─ CRITICAL / FAIL_FIXABLE >5 → STOP, lapor user
```

**Reuse prompt V4.9** (path absolute, gak perlu duplikat di v7/):
- `v49/BLIND_EXTRACT_PROMPT.md` — sesuaikan {photos_dir}, output ke `v7.1/_AUDIT_LOGS/{id}_blind.json` (bukan v49)
- `v49/AUDIT2_PROMPT.md` — output ke `v7.1/_AUDIT_LOGS/{id}_audit2.json`
- `v49/DECIDER_PROMPT.md` — output ke `v7.1/_AUDIT_LOGS/{id}_decider.md`
- `v49/SCHEMA_CHECKLIST.md` — kalau V7 nambah field baru, fork checklist ke `v7/SCHEMA_CHECKLIST.md` dan tunjuk ke fork itu di prompt.

**Spawn audit-blind di Step 0.5** (bersamaan dengan first batch Read main).

**Compare di Step 3.5** (main agent), **escalation di Step 3.6** (kalau ambiguous).

Detail flow audit + verdict rules: `v49/AUTORUN.md` Step 0.5, 3.5, 3.6 — identik untuk V7, hanya path output beda.

**NEVER skip audit gate** (enforcement 2026-05-08). Kalau context tipis → STOP + lapor user, lanjut session baru.

---

## V7-specific changes (in-progress)

V7 punya field tambahan / template baru yang belum di V4.5 — lihat `_PENDING_FIXES.md`, `AUDIT_NOTES.md`, `_AGENT2_HANDOVER.md`. Saat field baru ditambah, update `v7/SCHEMA_CHECKLIST.md` supaya audit gate tahu validate.

---

## Legacy V4.5 flow di bawah (basis V7) ↓↓↓

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
