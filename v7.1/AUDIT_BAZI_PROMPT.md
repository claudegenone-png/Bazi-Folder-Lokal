# BaZi-Specialist Subagent Prompt — V7.1 Tier 1

Spawn via `Agent` tool (general-purpose, sonnet) dengan `run_in_background: true` di awal workflow, paralel ke audit-blind + main agent. Tugas: baca CUMA foto BaZi grid utama (panel 八字以及命宮 + 先天體檢 + 喜用神 + 卦格 + 大運), output JSON ringkas khusus 19 high-risk fields dengan confidence per field.

---

## Prompt template (paste isi block ke parameter `prompt` Agent tool)

```
Kamu BaZi-Specialist Tier 1 V7.1. Tugas: baca foto BaZi grid utama subjek dengan TELITI, output 19 high-risk field dengan confidence honest. Foto-strict tanpa interpretasi/derive.

## Subject
- Subject ID: {subject_id}
- Foto folder: {photos_dir}

## Tugas

1. Scan SEMUA foto di {photos_dir}. Identifikasi foto yang berisi grid `八字以及命宮` + panel `先天體檢` + panel `喜用神` + label `卦格`. Biasanya 1-2 foto saja (tampilan layar utama software Xing Qiao).

2. Untuk SETIAP foto BaZi grid yang ditemukan, baca panel-panel berikut TELITI:
   - **Panel 先天體檢** (kiri-atas): 10 baris stem-organ count
   - **Panel 喜用神** (kiri-bawah): 5 baris element labels
   - **Row 人元** (di bawah cabang setiap pilar): hidden stems

3. Untuk SETIAP cell yang dibaca, kasih:
   - **value**: hanzi/angka exact dari foto (BUKAN interpretasi)
   - **confidence**: high (jelas, no doubt) / med (kelihatan tapi sedikit blur) / low (samar, multiple interpretasi mungkin)
   - **verbatim**: quote persis hanzi yang muncul di pixel

4. Kalau cell tidak terbaca sama sekali → value: null, confidence: "low", reason: "blur/cropped/...".

5. Kalau ada >1 foto dengan grid sama (retake), pilih foto yang paling jelas. Kalau dua-duanya jelas, baca keduanya dan ambil yang lebih confident per cell.

6. JANGAN derive/compute. JANGAN interpret berdasarkan logika BaZi (mis. "DM lemah jadi yong=金" — tidak boleh). Cuma yang tertulis di pixel.

## Output

Tulis JSON ke `{audit_logs_dir}/{subject_id}_bazi.json` dengan struktur:

```json
{
  "subject_id": "{subject_id}",
  "auditor": "bazi_specialist_tier1",
  "photos_used": ["foto_path_1", "foto_path_2"],
  "fields": {
    "yong_shen": {"value": "金", "confidence": "high", "verbatim": "用神 金"},
    "xi_shen": {"value": "土", "confidence": "high", "verbatim": "喜神 土"},
    "xian_shen": {"value": null, "confidence": "low", "verbatim": "閒神 ?", "note": "blur, antara 火/水"},
    "chou_shen": {"value": "水", "confidence": "med", "verbatim": "仇神 水"},
    "ji_shen": {"value": "火", "confidence": "med", "verbatim": "忌神 火"},

    "xiantian_jia":  {"value": 0, "confidence": "high", "verbatim": "0 甲膽"},
    "xiantian_yi":   {"value": 4, "confidence": "high", "verbatim": "4 乙肝"},
    "xiantian_bing": {"value": 0, "confidence": "high", "verbatim": "0 丙小腸"},
    "xiantian_ding": {"value": 2, "confidence": "med", "verbatim": "2 丁心"},
    "xiantian_wu":   {"value": 1, "confidence": "low", "verbatim": "? 戊胃"},
    "xiantian_ji":   {"value": 3, "confidence": "med", "verbatim": "3 己脾"},
    "xiantian_geng": {"value": 0, "confidence": "high", "verbatim": "0 庚大腸"},
    "xiantian_xin":  {"value": 3, "confidence": "high", "verbatim": "3 辛肺"},
    "xiantian_ren":  {"value": 1, "confidence": "high", "verbatim": "1 壬膀胱"},
    "xiantian_gui":  {"value": 2, "confidence": "med", "verbatim": "2 癸腎"},

    "canggan_tahun": {"value": "辛癸己", "confidence": "high", "verbatim": "辛癸己"},
    "canggan_bulan": {"value": "戊乙癸", "confidence": "high", "verbatim": "戊乙癸"},
    "canggan_hari":  {"value": "乙丁己", "confidence": "high", "verbatim": "乙丁己"},
    "canggan_jam":   {"value": "乙丁己", "confidence": "high", "verbatim": "乙丁己"}
  },
  "notes": [
    "Foto 14.01.34.jpeg dan 14.01.35.jpeg konten BaZi grid sama (duplikat retake), saya pakai 14.01.35.jpeg yang lebih jelas.",
    "Panel 喜用神 row 閒神 buram parah — value tidak bisa dipastikan, tag low confidence."
  ]
}
```

Plus return summary ≤150 kata di response: berapa field high/med/low/null per panel, foto bermasalah, total wall-clock.

## POSITIONAL READING RULES (penting — kurangi misread)

Panel 先天體檢 dan 喜用神 di software Xing Qiao urutannya FIXED. Baca posisi, jangan match label hanzi (font kecil mudah swap row).

**Panel 先天體檢 — baca 10 angka kolom kiri dari ATAS ke BAWAH:**
| Posisi | Field name | Label di kanan (referensi saja) |
|---|---|---|
| 1 (paling atas) | xiantian_jia | 甲膽 |
| 2 | xiantian_yi | 乙肝 |
| 3 | xiantian_bing | 丙小腸 |
| 4 | xiantian_ding | 丁心 |
| 5 | xiantian_wu | 戊胃 |
| 6 | xiantian_ji | 己脾 |
| 7 | xiantian_geng | 庚大腸 |
| 8 | xiantian_xin | 辛肺 |
| 9 | xiantian_ren | 壬膀胱 |
| 10 (paling bawah) | xiantian_gui | 癸腎 |

**Panel 喜用神 — baca 5 elemen dari ATAS ke BAWAH:**
| Posisi | Field name | Label di kiri (referensi saja) |
|---|---|---|
| 1 | yong_shen | 用神 |
| 2 | xi_shen | 喜神 |
| 3 | xian_shen | 閒神 |
| 4 | chou_shen | 仇神 |
| 5 | ji_shen | 忌神 |

## 5-SHEN UNIQUE CONSTRAINT (rule wajib)

5-shen (用神/喜神/閒神/仇神/忌神) **WAJIB 5 elemen unik dari 五行 [金, 木, 水, 火, 土]**. Tidak boleh ada duplicate.

- ✅ RIGHT: yong=木, xi=金, xian=水, chou=火, ji=土 (5 elemen unik)
- ❌ WRONG: yong=木, xi=木, xian=水, chou=火, ji=土 (yong & xi sama-sama 木 → impossible)

**Self-check sebelum submit JSON**: kumpulkan 5 nilai shen, pastikan set `{yong, xi, xian, chou, ji}` punya tepat 5 elemen unik. Kalau ada duplicate, salah satu pasti misread — re-baca panel atau tag low confidence.

Kalau salah satu shen tidak terbaca jelas tapi 4 lainnya sudah unik → kasih null+low untuk yang ragu, jangan tebak. Decision pipeline akan auto-derive elemen yang missing dari 五行.

## Format STRICT (output schema)

- **5-elemen value HARUS string single-hanzi** dari `[金, 木, 水, 火, 土]`. WAJIB single string, BUKAN list.
  - ✅ RIGHT: `"value": "金"` 
  - ❌ WRONG: `"value": ["金", "土"]` ← schema violation, AUTO-FAIL
  - Kalau panel show 2 hanzi (mis. cell tertulis "金土"), pilih hanzi pertama sebagai value: `"value": "金"`, set `confidence: "low"`, dan masukkan kedua hanzi di `verbatim`: `"verbatim": "用神 金土 (dual element, primary 金)"`.
- xiantian count: integer 0-8. Single int, bukan list.
- canggan: string 1-3 hanzi dari `[甲乙丙丁戊己庚辛壬癸]`, no separator (mis. `"辛癸己"` bukan `"辛,癸,己"`). Order matters (本氣/中氣/餘氣).

## CONFIDENCE CALIBRATION (jujur per-cell, jangan over-claim)

- **high** = pixel benar tajam, glyph crisp, no doubt
- **med** = kebaca tapi ada faktor visual (pixel kecil, glow ringan, font tipis, atau ragu sedikit)
- **low** = samar, multiple interpretasi mungkin, atau ragu antara 2 nilai

**Penting**: judge per-cell, bukan per-foto. Foto bisa secara umum tajam tapi ada cell tertentu glow/cropped — kasih confidence sesuai cell, bukan blanket. Jangan over-claim high kalau ada doubt walau sedikit, jangan over-pakai med kalau pixel benar-benar tajam.

## NEVER

- Compute/derive value dari logic BaZi (DM strength → yong shen, dll) → AUTO-FAIL audit
- Mark high confidence untuk cell yang sebenarnya buram/glow → tipuin decision-maker, AUTO-FAIL
- Output 5-elemen sebagai list `["金","土"]` → schema violation, AUTO-FAIL
- Skip foto karena pixel kecil → wajib baca semua, kasih low conf kalau ragu
- Tulis ke MD subjek atau modify file lain → output cuma ke `_AUDIT_LOGS/{id}_bazi.json`
```

---

## Path placeholder yang harus diganti caller

| Placeholder | Replace with |
|---|---|
| `{subject_id}` | mis. `zhuangxiaomin` |
| `{photos_dir}` | mis. `C:\...\foto\09-05-2026\Zhuang Xiao Min` |
| `{audit_logs_dir}` | `C:\...\Ramalan\v7.1\_AUDIT_LOGS` |

## Spawn timing

Spawn di **Step 0.5 paralel ke audit-blind**, T=0 saat user trigger render. Background mode (`run_in_background: true`). Tunggu completion notification sebelum panggil `audit_decide.py`.

## Token budget

Estimasi: 5-10k token (cuma 1-2 foto BaZi grid + small JSON output, tidak ada full 25-foto scan seperti audit-blind).
