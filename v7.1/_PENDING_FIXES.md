# Pending Fixes — V4.5 FULL-MD MODE

**Last update:** 2026-05-07 (sore)
**Status:** ✅ PRODUCTION-READY untuk daily render

---

## ✅ Resolved (this session)

### Engine Side
| # | Bug | File | Fix |
|---|-----|------|-----|
| 1 | Marriage list di-trim ke 3 | `parse_md.py` | `[:3]` cap removed, foto persis |
| 2 | "None · None" leak di marriage tag | `render.py` | Null-safe rel_label + reason |
| 3 | Shio fallback year_branch | `build_from_ocr.py` | Strict MD `shio_hz` only |
| 4 | Marriage relationship_hz hardcoded None | `build_from_ocr.py` | Default 六合/六沖 untuk visualisasi, MD override |
| 5 | Gender hardcode "Wanita"→陰女 | `parse_md.py` | Prefer MD `gender_hz`, raw fallback |
| 6 | Michele HTML comment leak | `templates/page_06_daymaster.html` | Generic comment |
| 7 | Da Yun cycles recompute dari month_pillar | `build_from_ocr.py` | Pull MD `da_yun` list langsung |
| 8 | Ten god per cycle deterministic only | `parse_md.py` + `build_from_ocr.py` | MD `:ten_god` suffix support, deterministic fallback |
| 9 | Workflow agent skip Step 4 build PDF | `AUTORUN.md` | Step 4 explicit "WAJIB JALANKAN" |
| 10 | Page 4 + Page 6 wuxing tampil persen | `render.py` | Raw count integer dari MD |
| 11 | Wheel cocok kuning subtle | `render.py` | Hijau (#2D6A4F) line + cell |
| 12 | Self position di-override marriage list | `render.py` | Self protected dari override |

### Schema MD Updates (WEB_CLAUDE_PROMPT.md)
| Field | Note |
|-------|------|
| `shio_hz` | Foto label `屬X` di main BaZi grid |
| `gender_hz` | Foto Zi Wei header `陽女`/`陰男`/dll |
| `marriage_*_relationships` | Optional kategori 三合/六合/沖/害/刑 kalau foto group |
| `da_yun` extended | Format kaya `10:丙辰:正印, 20:乙卯:偏印, ...` (ten god optional) |
| Yang Zhai gua strict no-derive | Eksplisit dari label `○震卦`/`○離卦`, jangan derive arah hunian |
| Zi Wei chart reading warning | Tips baca grid padat, hindari salah pilih main star |
| 5-shen `xi_yong_shen`, `xian_shen`, `chou_shen` | DATA fields baru — foto NCC main grid kasih 5-kategori |
| `shi_shen_per_pilar_*` | Promoted ke DATA section — 十神 label per pilar dari foto |
| `ming_gong_bazi` | Promoted ke DATA — 命宮 stem-branch dari foto main grid |
| `shen_sha_list` optional @ tag | Format dual: `天乙貴人@日` (kalau foto kasih pilar) atau `驛馬` only (foto flat) |
| Industri rule strict | Wajib ambil dari foto 事業 list, no fabricate dari yong_shen logic |
| Anti-fabrication rule | Section creative wajib grounded di DATA, no fabricate bidang/profesi/aktivitas |

---

## 🟡 Extraction-side (re-extract per subject untuk update)

Subjek yang punya bug extraction sudah ada record validation report. Bug field per subject tergantung kualitas extraction. Untuk subjek lama (chelsey/keiko/wuhuanyang/banzi2/dll), MD format lama belum punya field FULL-MD baru. Kalau di-build, field-field baru tampil "—" — itu EXPECTED, bukan regression.

**Action:** Re-extract dengan prompt schema baru di window Claude Code daru, prompt format `(path foto) pakai V4.5`.

---

## 📋 Daily Render Sekarang Aman

Production workflow:
1. Window baru Claude Code
2. User type: `(path foto folder) pakai V4.5`
3. Agent baca AUTORUN.md → eksekusi 5 step otomatis
4. Output: PDF di `#result/{date}/{Name}-{Hanzi}-{Birth}.pdf` + chat report

Tidak ada lagi engine compute formula yang konflik dengan foto NCC. Semua data dari MD.
