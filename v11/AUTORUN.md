# AUTORUN V11 — Engine Hemat Paralel (Sonnet, no-audit)

**Trigger:** `{path foto} pakai V11`
**Anti-ketukar:** echo `MODE: V11 (hemat, no-audit)` di baris pertama. Ragu → tanya.
**Model:** Sonnet semua. Subagent wajib `model:"sonnet"`.

---

## Folder split (user organisir sebelum kirim path)

**Root folder** — arsip saja, AI TIDAK baca dari file:
- BaZi grid, 命宮, shio → dikirim via **prompt attachment**

**data/ (~13 foto)** — Main baca + ekstrak DATA + terjemah liu nian/gushu:
- ZiWei chart (2-3 foto)
- Da Yun table (流年易鑑表)
- 婚配 (marriage shio list)
- 陽宅 (yang zhai gua)
- 神煞 (shen sha list)
- 流年 prose 6 tahun
- 古書云 quotes
- **Foto tambahan / tidak dikenal → taruh di sini**

**transelate/ (~11 foto)** — Translator baca + terjemah:
- 11 palace narasi (兄弟/夫妻/子女/財帛/疾厄/遷移/僕役/官祿/田宅/福德/父母) — **bukan 命宮** (sudah via prompt)
- 性情 / 全局總論 / 事業 / 財富 BaZi wealth

---

## Pipeline

### PRE-FLIGHT — Cek foto wajib (SEBELUM apapun)

User WAJIB kirim **3 screenshot langsung di prompt** (sebagai image attachment), bukan dari file:
- **BaZi grid** (4 pilar + 先天體檢 + 喜用神 + DM旺度 + Da Yun row)
- **命宮 ZiWei narrative**
- **Shio** (kalau tidak terlihat di BaZi grid, kirim screenshot terpisah)

Format trigger: `{path} pakai V11` + attach 3 foto tersebut di prompt yang sama.

AI baca 3 foto dari **prompt context** (0 extra tool call) → ekstrak data critical + 命宮 langsung.
File asli di root folder = arsip saja, **AI TIDAK baca dari file system**.

Kalau salah satu dari 3 foto tidak di-attach di prompt → **STOP, ingatkan user singkat.** Jangan lanjut.

---

### Step 0 — Rename
```
cd C:\Users\sukam\OneDrive\Documents\Ramalan\v11
python rename_photos_sequential.py "<photos_dir>"
```
Output: data/1..N, transelate/N+1..M. Foto di root folder = arsip, diabaikan (tidak di-rename, tidak ada WARN).

---

### Step 0.5 — Validasi folder (WAJIB, sebelum spawn)
Scan sekilas kedua folder:
1. **Foto salah tempat** → pindahkan + re-run rename sebelum lanjut
   - data/ = struktur/list: BaZi, ZiWei, da yun table, 婚配, 陽宅, 神煞, 流年, 古書
   - transelate/ = narasi panjang: 12 palace, 性情, 全局, 事業, 財富
2. **Foto tambahan** → masuk data/
3. **Foto buram** → STOP, lapor nomor foto, tunggu crop user → lanjut

---

### Step 1 — Spawn paralel T=0

**MAIN** — dari prompt context + baca data/:
- BaZi grid + 命宮 + shio: **sudah ada di context dari prompt** → ekstrak langsung, TIDAK baca ulang dari file
- Baca sisa foto di data/ (ZiWei chart, Da Yun table, 婚配, 陽宅, 神煞, 流年, 古書, dll)
- Terjemah liu_nian + gushu inline
- **Langsung tulis `## DATA` ke MD** (tidak nunggu translator)

**TRANSLATOR** (spawn background, Sonnet):
- Baca transelate/ (11 palace — tanpa 命宮)
- Terjemah 11 palace + 性情/全局/事業/財富 faithful & penuh
- Output ke: `_AUDIT_LOGS/tafsir_{id}.json` dengan struktur:
```json
{
  "palace_xiongdi_insight": "...",
  "palace_fuqi_insight": "...",
  "palace_zinu_insight": "...",
  "palace_caibo_insight": "...",
  "palace_jie_e_insight": "...",
  "palace_qianyi_insight": "...",
  "palace_puyi_insight": "...",
  "palace_guanlu_insight": "...",
  "palace_tianzhai_insight": "...",
  "palace_fude_insight": "...",
  "palace_fumu_insight": "...",
  "xingqing_poin": ["...", "..."],
  "overview_cards": ["Label | teks", "..."],
  "shiye_favorable_full": "...",
  "shiye_supportive_full": "...",
  "caibo_tafsir": "..."
}
```

---

### Step 2 — Merge + tulis MD lengkap
Setelah translator selesai → main baca `_AUDIT_LOGS/tafsir_{id}.json` → gabungkan ke MD.

**Disiplin akurasi WAJIB:**
- RULE 7: setiap palace insight HANYA dari foto palace yang cocok persis
- 12 palace PENUH & faithful — klausa kondisional dipertahankan — klausa ≥80% (命宮 ≥95%)
- 5-shen wajib 5 elemen unik [金木水火土]
- Field ragu → `null` + CATATAN

**RULE 7 source binding:**
| Field | Foto WAJIB | DILARANG |
|---|---|---|
| palace_ming_gong_insight | 【命宮】 | 全局/palace lain |
| palace_xiongdi_insight | 【兄弟】 | 全局 |
| palace_fuqi_insight | 【夫妻】 | 全局/婚配 |
| palace_zinu_insight | 【子女】 | 全局/fumu |
| palace_caibo_insight | 【財帛】 | 全局 |
| palace_jie_e_insight | 【疾厄】 | 全局 |
| palace_qianyi_insight | 【遷移】 | 全局 |
| palace_puyi_insight | 【僕役】 | 全局 |
| palace_guanlu_insight | 【官祿】 | 事業 foto |
| palace_tianzhai_insight | 【田宅】 | 全局 |
| palace_fude_insight | 【福德】 | 全局 |
| palace_fumu_insight | 【父母】 | 全局 |
| liu_nian_YYYY | Foto tahun YYYY | foto tahun lain |

**Schema:** WEB_CLAUDE_PROMPT.md / contoh donny_c.md (v11/data/subjects/).
- 性情 → `### Kepribadian Detail` (`poin:` list)
- 全局總論 → `### Sekilas Hidup` (`card:` "Label | teks")
- liu_nian/gushu/shiye/ziwei_su_ming → flat key di `## DATA`
- Bintang palace low-conf → `star: null` (insight tetap penuh)

**陽宅 (Yang Zhai) — WAJIB tulis DATA fields + TAFSIR:**

DATA fields (dari foto 陽宅, 6 zona):
```
- yang_zhai_zone_rumah_hz: 東北, 西南   ← orientasi rumah auspicious
- yang_zhai_zone_rumah_note: Rumah duduk ... menghadap ...
- yang_zhai_zone_pintu_hz: 西北, 西南, 東北, 西
- yang_zhai_zone_pintu_note: Pintu membuka ke ...
- yang_zhai_zone_dapur_hz: 東南
- yang_zhai_zone_dapur_note: Kompor di tenggara menghadap ...
- yang_zhai_zone_kamar_hz: 南, 西北, 西, 東北
- yang_zhai_zone_kamar_note: Kamar tidur di ...; ranjang di ...
- yang_zhai_zone_altar_hz: 東北, 西南, 西北, 西
- yang_zhai_zone_altar_note: Altar di ...
- yang_zhai_zone_kamar_mandi_hz: 東, 南, 北
- yang_zhai_zone_kamar_mandi_note: WC di ...
```
Keys valid: `rumah / pintu / dapur / kamar / altar / kamar_mandi`

TAFSIR fallback (jika DATA fields tidak ada): tulis `### Yang Zhai (Feng Shui Hunian)` dengan `zones:` list, engine otomatis convert. Tapi DATA fields lebih direkomendasikan — lebih eksplisit dan tidak bisa salah key.

JANGAN isi `zones:` dengan field `pills:` — tidak dipakai dan tidak ditampilkan.

**Palace TAFSIR — format wajib:**
```
### Palace Detail 1
ming_gong:
- star: [bintang utama atau null]
- insight: [terjemahan penuh]
- action: [1 kalimat saran aksi]

xiongdi:
...
zinu:
...
fuqi:
...

### Palace Detail 2
caibo: / jie_e: / qianyi: / puyi:

### Palace Detail 3
guanlu: / tianzhai: / fude: / fumu:
```
JANGAN pakai `palace1:` / `palace2:` — engine tidak mengenali format itu.

---

### Step 3 — Build
```
cd C:\Users\sukam\OneDrive\Documents\Ramalan\v11
python build_pdf.py {id}
```
Lapor: path PDF, size, pages, quality report foto.

---

## Checklist production (0 error)
- [ ] 3 foto (BaZi grid, 命宮, shio) di-attach di prompt
- [ ] rename_photos_sequential.py jalan
- [ ] Validasi folder: foto di tempat benar
- [ ] Translator output `tafsir_{id}.json` terbentuk
- [ ] build_pdf PASS (preflight 0 errors)
- [ ] Post-render preflight PASS (0 BLEED/ZONE?)

---

## Summary vs V7.1
| | V7.1 | V11 |
|---|---|---|
| Agen audit | 10 | **0** |
| Agen translator | 1 (baca ulang foto) | **1 (transelate/ only)** |
| BaZi grid + 命宮 | baca dari file | **dari prompt attachment (0 tool call)** |
| Main idle? | ya | **tidak** |
| Baca foto duplikat | ya (2×) | **tidak (0×)** |
| Model | Sonnet | **Sonnet** |
| Hemat token | — | **~70-80%** |
