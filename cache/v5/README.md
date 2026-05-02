# V5 — Yiteng Clone Engine + No-Photo PDF Pipeline

**Goal:** replikasi software 倚天 V2.6 (Taiwan) 100%; user input nama+tanggal+jam+gender → chart.json → PDF.

**Isolation policy:** V3 / V4.3 / V4.5 LOCKED daily-render — JANGAN modify. V5 self-contained di `cache/v5/`.

## Status (Phase 1 + Phase 2 partial)

### ✅ Selesai
- **Reference data**: 10 subjek Yiteng GT extract di `reference/` (~120 + 205 screenshots di-OCR)
- **Schema + formula reverse-engineering**: `reference/yiteng_schema.md` + `formula_v2_with_10_samples.md`
- **Engine module** `engine/`:
  - `bazi_minggong.py` — BaZi 命宮 custom 子平 月將 formula (8/8 = **100%** match Yiteng)
  - `scoring.py` — 旺度 / 體檢 / 五行 旺相死囚休 / 卦格 / 喜用神
  - `compute_chart.py` — unified producer (chart.json output)
  - test_pillars.py / test_dayun.py / test_ziwei.py / test_sihua.py — verification scripts
- **Verified 100% match** vs Yiteng GT untuk:
  - 4 pilar BaZi (10/10)
  - 大運 干支 sequence (90/90 cycles × 9 subjek)
  - Zi Wei 命宮 / 身宮 branch (6/6)
  - 命主 / 身主 / 五行局 (6/6)
  - 四化 placement (6/6)
  - BaZi 命宮干支 (8/8) — via custom 月將 formula
  - 12 palace + main star + brightness — spot-check verified

### ⚠️ Best-fit (proprietary Yiteng formula tidak bisa 100%)
- **旺度 numeric score**: direction OK, magnitude beda ~50% dari Yiteng (perlu Yiteng source code untuk match)
- **體檢 10-organ**: tally close, capping rule ~80% accurate
- **卦格 / 用事**: standard 月柱 mapping ~75%
- **喜用神**: lookup partial (perlu full 120-entry 窮通寶鑑 table)

### ⏳ Pending (untuk sesi terpisah)
1. **Adapter** `chart.json` → V4.5-format `subject.json` — rebuild `build_from_ocr.py` logic without OCR
2. **Narrative source** — V4.5 narasi datang dari OCR Yiteng. V5 perlu generate via Claude API atau template-lookup (TBD)
3. **End-to-end PDF render** — pakai V4.5 templates (sudah dicopy ke `templates/`)
4. **CLI wrapper** `cli.py` — `python cli.py "Nama" "1995-07-22" "14:00" "F"` → PDF

## Folder structure

```
cache/v5/
  engine/
    bazi_minggong.py    ← 命宮 custom formula
    scoring.py          ← 旺度/體檢/卦格/五行
    compute_chart.py    ← unified producer (entry point)
    test_*.py           ← verification scripts
    render.py / lookups.py / build_subject.py / compute_pillars.py  ← copied from V4.5 (read-only ref)
  reference/
    *_yiteng_extract.md  ← 10 subjek ground truth
    yiteng_schema.md
    formula_v2_with_10_samples.md
  templates/             ← copied from V4.5 (24 HTML files)
  assets/                ← copied from V4.5
  output/
    michele.json         ← sample chart.json
```

## Usage (current)

```bash
cd cache/v5/engine
python compute_chart.py "Michele" "1995-07-22" "14:00" "F" --out ../output/michele.json
```

Output: full chart.json with BaZi (4 pilar/命宮/大運/旺度/體檢/卦格) + Zi Wei (12 palace/main star/brightness/四化/命主/身主).

## Dependencies

```bash
pip install lunar-python py-iztro
```
