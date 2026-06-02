# V7.1 — AUDIT MARRIAGE (Triple-Vote untuk Halaman Shio/Marriage)

## Konteks
Marriage page (`page_marriage.html`) di V7.1 menampilkan tabel **cocok vs hindari** berdasarkan shio. Field ini WAJIB dari foto layar `婚配` di software Xing Qiao. **Reading error di halaman ini paling sering terjadi** karena layout foto biasanya kompak (multiple tiers di satu panel).

Tujuan prompt ini: agen membaca **hanya panel 婚配** dengan strict structured output untuk triple-vote.

## Input
- `{photo_path}` — foto layar 婚配 (full original, jangan crop)
- `{subject_id}` — ID subjek
- `{slot}` — A / B / C (untuk Tier 1) atau D / E (Tier 2)
- `{audit_logs_dir}` — folder output

## Output
File JSON di `{audit_logs_dir}/marriage_{subject_id}_{slot}.json` dengan schema:

```json
{
  "subject_id": "bpa",
  "slot": "A",
  "photo_path": "...",
  "tier_blocks": [
    {
      "tier_label_hz": "大吉",
      "tier_label_id": "Sangat Cocok / Hindari / Cocok / Hindari Berat",
      "shios_hz": ["鼠", "蛇", "雞"],
      "shios_branch": ["子", "巳", "酉"],
      "shios_count": 3,
      "prose_hz_verbatim": "天作良緣, 必定家聲克振, 富豪門牆, 心地純良美貌, 家室富有, 安寧和睦多福多德, 廬居安樂始終吉慶...",
      "prose_id_paraphrase": "Jodoh ditakdirkan langit, pasti nama baik keluarga gemilang, rumah tangga setara hartawan, hati tulus & rupawan, ..."
    },
    {
      "tier_label_hz": "忌",
      "tier_label_id": "Hindari",
      "shios_hz": ["龍", "馬", "羊", "狗"],
      "shios_branch": ["辰", "午", "未", "戌"],
      "shios_count": 4,
      "prose_hz_verbatim": "有吉亦有凶, 甘苦相並, 無進取之氣象, 內心多憂苦慘, 終必破敗...",
      "prose_id_paraphrase": "Ada baik ada buruk, manis-pahit campur, tidak ada semangat untuk maju, batin penuh kekhawatiran, akhirnya pasti runtuh..."
    }
  ],
  "confidence": "high",
  "issues": []
}
```

## Aturan extraction (HARD RULES)

### 1. WAJIB baca tier label di foto verbatim
Foto 婚配 biasanya punya 2-4 tier label:
- `大吉` / `吉` / `次吉` (cocok tier)
- `忌` / `凶` (hindari tier)
- Kadang `吉凶相半` (mixed) — TREAT AS COCOK dengan deskripsi mixed

JANGAN buat tier sendiri. Salin label hanzi persis dari foto.

### 2. Shio extraction MUST be exact
Untuk SETIAP tier:
- Tulis shio dalam bentuk **hanzi shio** (鼠/牛/虎/兔/龍/蛇/馬/羊/猴/雞/狗/豬)
- Convert ke **branch** (子/丑/寅/卯/辰/巳/午/未/申/酉/戌/亥)
- `shios_count` = panjang list

JANGAN tebak count. Hitung manual dari foto.

### 3. Prose verbatim WAJIB
- `prose_hz_verbatim` = salin teks hanzi panjang yang menjelaskan konsekuensi tier ini, **TANPA UBAH** (titik, koma, urutan).
- `prose_id_paraphrase` = parafrase Indonesia natural, max 80 kata per tier.
- JANGAN gabung 2 tier jadi satu prose. JANGAN pindah kalimat antar tier.

### 4. Konsistensi mutual exclusion
- Set shios di tier cocok ∩ tier hindari = ∅
- Total semua shios ≤ 12 (jangan duplikat shio antar tier)

### 5. Confidence labels
- `"high"` = semua tier label jelas, semua shio terbaca, prose lengkap
- `"med"` = 1-2 hanzi prose buram, tapi shio + tier label jelas
- `"low"` = ada tier yang shio-nya tidak yakin, atau prose 50%+ tidak terbaca

## Larangan ABSOLUT
- ❌ JANGAN derive dari day branch (三合/六合/六沖/六害)
- ❌ JANGAN gunakan kaidah BaZi untuk infer cocok/hindari — semuanya dari foto layar
- ❌ JANGAN gabung tier label (e.g. "大吉/吉" jadi satu) — terpisah per blok
- ❌ JANGAN translate shio Hanzi ke nama Indonesia di field `shios_hz` — itu untuk `prose_id_paraphrase` saja
- ❌ JANGAN tulis prose dari template/training data — jika foto tidak ada, tulis `prose_hz_verbatim: null`

## Decision logic (audit_decide.py side)
Setelah 3 slot (A/B/C) selesai:
- 3/3 agreement (shios_branch + tier_label_hz) → PASS dengan high confidence
- 2/3 agreement → PASS dengan majority decision
- 0-1/3 agreement → ESCALATE Tier 2 (slot D + E) → re-vote dengan 5 readings
- Tier 2 masih disagree → STOP, user retake foto

Field yang di-check untuk consensus:
1. `shios_branch` per tier (set equality)
2. `tier_label_hz` (string match)
3. `shios_count` per tier
4. (NOT prose — prose accepted dari slot dengan confidence "high")
