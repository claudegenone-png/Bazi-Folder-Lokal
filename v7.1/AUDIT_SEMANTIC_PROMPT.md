# V7.1 — AUDIT SEMANTIC (Translation Flip & Star Name Detection)

## Konteks
Setelah Step 3 (MD ditulis) tetapi sebelum Step 4 (build), spawn **1 verifier agent** untuk semantic cross-check antara MD field dengan foto sumbernya. Tujuan: catch 2 jenis bug yang TIDAK terdeteksi oleh shape preflight:

1. **Translation flip** — negation reversed (mis. "tidak sepenuhnya memahami" vs aktual "sepenuhnya memahami")
2. **Hanzi swap** — star/term confusion (mis. `天日` vs aktual `天同`)
3. **Fact contradiction** — Kesimpulan narrative menyebut data yang konflik dengan DATA fields (mis. format=偏官格 di DATA tapi kesimpulan bilang 正官格)

Verifier ini **LLM-as-judge** — agen baca foto + MD spot-check, jawab match per item.

## Input
- `{photo_dir}` — folder foto subjek (path absolute)
- `{md_path}` — path ke `v7.1/data/subjects/{id}.md`
- `{audit_logs_dir}` — folder output

## Field yang di-check (HIGH-IMPACT)
Baca DATA section MD, identifikasi pasangan field ↔ foto sumber:

| MD field | Foto source | Check |
|---|---|---|
| `marriage_cocok` + `marriage_hindari` | foto 婚配 | shios sesuai tier, no overlap |
| `marriage_cocok_tafsir` | foto 婚配 prose | semantic match, no negation flip |
| `marriage_hindari_tafsir` | foto 婚配 prose | semantic match, no negation flip |
| `palace_ming_gong_insight` | foto 命宫 | prose narrasi match foto, NO ringkasan, NO halusinasi |
| `palace_fumu_insight` | foto 父母 | semantic match (sering negation flip) |
| `ziwei_ming_gong` (star) | foto 紫微 panel | star name hanzi exact match |
| `format` | foto BaZi header | label match exact |
| `yong_shen` + `ji_shen` | foto 用神/喜神 | label match, no overlap |
| `gushu_quotes[].text_id` | foto 古書云 | translation match Indonesian-Hanzi |
| `kesimpulan_narrative` | (synthesized) | konsisten dengan DATA (format, yong/ji, marriage tier) |

## Output
File `{audit_logs_dir}/semantic_{subject_id}.json`:

```json
{
  "subject_id": "bpa",
  "n_checks": 15,
  "verdicts": [
    {
      "field": "palace_fumu_insight",
      "foto_source": "父母 prose foto",
      "verdict": "MATCH",
      "evidence": "MD prose mencakup '事實上他們完全了解' = 'sepenuhnya memahami' — OK"
    },
    {
      "field": "ziwei_ming_gong",
      "foto_source": "紫微 ming_gong panel",
      "verdict": "MISMATCH",
      "evidence": "MD bilang star=天日, foto menunjukkan 天同 (Tian Tong)",
      "severity": "high"
    },
    {
      "field": "kesimpulan_narrative",
      "foto_source": "(synthesized, cross-check DATA)",
      "verdict": "INTERNAL_CONFLICT",
      "evidence": "Kesimpulan menyebut 'Pejabat Tujuh' (偏官格) — konsisten dengan DATA.format ✓",
    }
  ],
  "summary": {
    "MATCH": 12,
    "MISMATCH": 2,
    "INTERNAL_CONFLICT": 0,
    "UNVERIFIABLE": 1
  },
  "high_severity_count": 2,
  "recommendation": "FIX_BEFORE_BUILD" 
}
```

## Verdict types
- `MATCH` — MD prose/value semantic match foto. ✓
- `MISMATCH` — MD value beda dengan foto. Severity:
  - `high` — wrong fact (star name salah, marriage shio salah, negation flipped)
  - `med` — partial mismatch (prose extra detail not in foto, or short ringkas)
  - `low` — typo / stylistic difference
- `INTERNAL_CONFLICT` — MD field A vs MD field B contradict (e.g. format vs kesimpulan)
- `UNVERIFIABLE` — foto tidak jelas atau field synthetic (kesimpulan)

## Aturan extraction
1. **JANGAN ubah MD** — verifier ini READ-ONLY. Output rekomendasi saja.
2. **Foto authoritative** — kalau MD beda dengan foto, foto yang benar (kecuali foto blur)
3. **Negation/quantifier sensitivity** — perhatikan kata "tidak", "bukan", "完全/不", "sepenuhnya/sebagian", "akan/pasti vs mungkin"
4. **Hanzi character-level** — bedakan 日/同, 文昌/文曲, 太陰/太陽, 七殺/正官
5. **Skip kalau foto tidak ada** — verdict `UNVERIFIABLE`, jangan halusinasi

## Recommendation field
- `PROCEED` — semua MATCH atau low-severity → build OK
- `FIX_BEFORE_BUILD` — ada high-severity MISMATCH → STOP, user/main agent perbaiki MD
- `MANUAL_REVIEW` — banyak UNVERIFIABLE atau ambiguous → user keputusan akhir

## Larangan
- ❌ JANGAN re-extract foto — tugasnya verify MD vs foto, BUKAN baca ulang full
- ❌ JANGAN paraphrase prose untuk "improvement" — fokus check fact-level match
- ❌ JANGAN output prose alternatif — output verdict + evidence saja
