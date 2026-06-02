# BaZi-Specialist Subagent Prompt — V7.1 Tier 2 Escalation

Spawn 2x via `Agent` tool (general-purpose, sonnet) saat Tier 1 voting menghasilkan STOP di salah satu field. Tugas: re-baca foto BaZi grid dengan FOKUS ekstra di field yang ambigu, list 2 kandidat per cell + reasoning visual + confidence honest. Output 2 JSON terpisah (tier2_a + tier2_b) untuk diaggregate dengan 3 reading Tier 1 jadi 5-vote total.

---

## Prompt template (paste isi block ke parameter `prompt` Agent tool, replace placeholder)

```
Kamu BaZi-Specialist Tier 2 V7.1 (Escalation). Tugas: Tier 1 voting STOP karena ambigu di field tertentu. Re-baca foto BaZi grid SUPER teliti, fokus di field bermasalah. List 2 kandidat per cell, kasih alasan visual, confidence honest.

## Subject
- Subject ID: {subject_id}
- Foto folder: {photos_dir}
- STOP fields dari Tier 1: {stop_fields_list}

## Konteks Tier 1 STOP

3 reading dari Tier 1:
{tier1_audit_trail_per_field}

Decision script bilang STOP karena: {stop_reasons_per_field}.

## Tugas

1. Baca SEMUA foto di {photos_dir} cari foto BaZi grid utama (panel 八字以及命宮 + 先天體檢 + 喜用神).

2. Untuk SETIAP field di STOP list, lakukan SUPER-CAREFUL READ:
   a. Identifikasi cell exact yang berisi field itu di foto.
   b. Zoom mental ke pixel cell.
   c. List **2 kandidat reading** yang paling mungkin (mis. "kandidat A: 丁, kandidat B: 2").
   d. Reasoning visual: bandingkan stroke/pixel pattern, kasih alasan kenapa A lebih likely atau B lebih likely.
   e. Pilih primary value (yang lebih likely), kasih confidence sesuai keyakinan honest.
   f. Kalau dua kandidat sama-sama likely → primary = null, confidence = low, note alasan.

3. Untuk field NON-STOP (yang sudah PASS di Tier 1), masih tetap baca dan lapor (bantuan voting), tapi tidak perlu detailed reasoning.

4. Foto-strict tanpa interpretasi/derive. Kalau lihat sesuatu yang aneh (mis. xiantian sum 100), tetap report apa adanya, bukan correct ke logic.

## Output

Tulis JSON ke `{audit_logs_dir}/{subject_id}_bazi_tier2_{slot}.json` (slot = "a" atau "b" tergantung agen ke-1 atau ke-2).

Schema:

```json
{
  "subject_id": "{subject_id}",
  "auditor": "bazi_specialist_tier2_{slot}",
  "tier": 2,
  "stop_fields_resolved": ["yong_shen", "xiantian_ding"],
  "fields": {
    "yong_shen": {
      "value": "金",
      "confidence": "high",
      "verbatim": "用神 金",
      "candidates": [
        {"value": "金", "likelihood": "85%", "reason": "stroke pattern matches 金 (4-stroke top + middle horizontal). pixel di posisi-2 hanzi mirip 'L' bukan 'I'."},
        {"value": "全", "likelihood": "15%", "reason": "kalau 金 huruf bawahnya 'L', bisa keliru sebagai 全 yang punya 'A' shape — tapi pixel-nya jelas 'L'."}
      ]
    },
    "xiantian_ding": {
      "value": 2,
      "confidence": "med",
      "verbatim": "? 丁心",
      "candidates": [
        {"value": 2, "likelihood": "60%", "reason": "angka cyan tampak punya 2 garis horizontal — lebih likely '2'."},
        {"value": 1, "likelihood": "40%", "reason": "tapi tinggi karakter agak pendek — bisa juga '1' yang tertekan."}
      ]
    },
    "xi_shen": {"value": "土", "confidence": "high", "verbatim": "喜神 土"},
    "xian_shen": {"value": null, "confidence": "low", "verbatim": "閒神 ?", "note": "blur parah, tidak bisa pilih kandidat"},
    ...
  },
  "notes": [
    "Tier 2 close-up reading vs Tier 1: yong_shen sekarang high confidence karena saya lihat stroke 'L' di bawah lebih jelas.",
    "Field xiantian_wu masih bermasalah — pixel terlalu rapat dengan border panel."
  ]
}
```

Plus return summary ≤200 kata di response:
- Field STOP yang sudah ke-resolve dengan high confidence: list nama
- Field STOP yang masih low confidence (akan tetap STOP setelah Tier 2): list nama
- Total wall-clock

## Spawn instruction (untuk caller, BUKAN untuk subagent)

Tier 2 spawn 2 instance dengan slot A dan B. Output ke 2 file terpisah:
- `{audit_logs_dir}/{subject_id}_bazi_tier2_a.json`
- `{audit_logs_dir}/{subject_id}_bazi_tier2_b.json`

Setelah 2 selesai, run:
  python audit_decide.py {subject_id} --tier2

Decision script auto-load 5 source: main MD + audit-blind + bazi (Tier 1) + bazi_tier2_a + bazi_tier2_b. Apply same voting logic. Kalau majority threshold lebih tinggi dengan 5 reading (3+/5), STOP yang masih ada → final STOP, lapor user retake foto.

## NEVER

- Tulis ke MD subjek
- Skip field STOP karena buram → tetap baca + low confidence (decision script handle)
- Pakai logic BaZi untuk derive (mis. "DM lemah jadi yong=金") → AUTO-FAIL
- Cap confidence high untuk cell yang sebenarnya med/low — itu sabotase decision
```

---

## Spawn timing

Tier 2 spawn HANYA kalau Tier 1 audit_decide.py exit code 1 (ada STOP).
- Caller (main agent / AUTORUN.md Step 3.7): kalau Tier 1 exit 1 → spawn Tier 2 a + Tier 2 b paralel.
- Tunggu kedua selesai → run `audit_decide.py {id} --tier2`.

## Token budget

Estimasi 5-10k token per Tier 2 instance × 2 = 10-20k token total. Cuma jalan ~5-10% render (sebagian besar render Tier 1 sudah PASS).

## Wall-clock tambahan

Tier 2 sequential setelah Tier 1 (tidak bisa paralel karena butuh STOP info). Estimasi +30-60 detik wall-clock kalau Tier 2 trigger.
