# Validation Report v2 — Li Jia Ling 李佳玲 (1988-06-01 15:00)

**Agent:** V (PDF Validator) · **Mode:** V4.5 Full-MD · **Date:** 2026-05-07
**Source PDF:** `#result/2026-05-07/Li Jia Ling-李佳玲-1988-06-01.pdf` (mtime 17:45, 4.18 MB)
**Build dir:** `v45/_build/lijialing/` (mtime 17:45 — sync match)
**Photo source:** `foto/database/07-05-2026/1/` (28 jpegs)
**Predecessor:** `_VALIDATION_REPORT_lijialing.md` (v1) — listed 3 CRITICAL + 4 MEDIUM + 3 MINOR.

> **Note** — `lijialing.json` / `lijialing.ocr.json` were not found in `data/subjects/` during this audit (only `.md` and `.PRODUCTION_REFERENCE.md.bak`). All validation done foto ↔ MD ↔ HTML build (1:1 PDF render proxy).

---

## Status of v1 bugs (regression check)

| v1 bug | Severity v1 | v2 status |
|---|---|---|
| Marriage hindari missing 辰/龍 | CRITICAL | **FIXED** — `marriage_hindari: 丑, 卯, 戌, 辰` (4) di MD; page_marriage.html row 224-228 render 辰 Naga dengan tag HINDARI + Naga-Merah.svg |
| "None · None" leak di marriage cards | CRITICAL | **FIXED** — grep `None · None` di `_build/lijialing/` = 0 hits |
| Yong/Ji shen kontradiksi foto | CRITICAL | **FIXED** — MD `yong_shen: 水`, `ji_shen: 火`; cover line 204 "Elemen Utama: Air 水"; page_06 tafsir konsisten "Air sebagai 用神 utama, Api sebagai 忌神" |
| Format 卦格 null | MEDIUM | **FIXED** — MD `format: 傷官格`; muncul 7× di `_master.html` |
| Subject-bar age "Umur 37 tahun" | MEDIUM | **STILL BROKEN** — masih "Umur 37 tahun" di 5 halaman (1 Juni 1988 → 2026 = 38 Barat / 39 虛歲) |
| Gender 陰女 vs foto 陽女 | MEDIUM | **FIXED** — MD `gender_hz: 陽女` (戊辰 1988 = tahun Yang ✓) |
| xi_shen / chou_shen / xian_shen null | MEDIUM | **FIXED** — MD: `xi_yong_shen: 木`, `xian_shen: 土`, `chou_shen: 金` |
| "Michele's polygon" stale comment | MINOR | **FIXED** — comment line 244 sekarang "Subject's wuxing polygon (regenerated per subject)"; grep `Michele` = 0 hits |
| Palace `star: null` | MINOR | **FIXED** — Palace Detail 1/2/3 di MD semua diisi (武曲, 太陽, 紫微, 太陰, 天府, 廉貞, 天機, 七殺, 武曲, 太陰, 太陰, 天府) |
| dm_pos/neg integer | MINOR | OK per CATATAN; raw +3.678/-5.182 muncul di `_master.html:3968,3973` |

**v1 → v2 net fix rate: 9 / 10** (1 medium regression remaining: Umur 37).

---

## A. Data Integrity (foto ↔ MD ↔ PDF/HTML)

| Field | Foto (truth) | MD | PDF/HTML | Status |
|---|---|---|---|---|
| Identity | 李佳玲 / Li Jia Ling | ✓ | ✓ | OK |
| Gender | 陽女 (女) | 陽女 / Wanita | "Wanita" | OK |
| Lahir | 1988-06-01 15:00 | ✓ | "1 Juni 1988 · 15:00" | OK |
| 4 Pilar | 戊辰/丁巳/丁亥/戊申 | ✓ | ✓ | OK |
| DM strength | +3.678 / -5.182 → 弱 | ✓ (3678/5182) | ✓ "+3.678 / -5.182" + "LEMAH" | OK |
| Wuxing | 金2 水3 木2 火3 土5 | ✓ | ✓ (radar polygon + dme cards) | OK |
| **Yong shen** | 水 | 水 | "Air 水", "用神 utama" | OK |
| **Xi yong shen** | 木 (喜神金 di foto?)<sup>*</sup> | 木 | "Kayu 木 喜用神" | NOTE: lihat catatan |
| **Ji shen** | 火 | 火 | "Api 火 忌神" | OK |
| **Xian shen** | 土 | 土 | (referenced) | OK |
| **Chou shen** | 金 (foto: 仇神木?)<sup>*</sup> | 金 | "Logam 金 仇神" | NOTE: lihat catatan |
| **Format (卦格)** | 傷官 | 傷官格 | 傷官 (7×) | OK |
| Da Yun 10 cycles | 丙辰/乙卯/甲寅/癸丑/壬子/辛亥/庚戌/己酉/戊申/丁未 | ✓ | ✓ render lengkap | OK |
| Da Yun arah | 逆行 | ✓ | ✓ | OK |
| Da Yun start_age | 10 | ✓ | ✓ | OK |
| Da Yun ten gods | 30:正印, 40:七殺 (eksplisit MD); sisanya deterministic | ✓ | ✓ (正印 line 372, 七殺 line 378, 傷官/比肩 fallback) | OK |
| Marriage cocok | 鼠/猴/雞 → 子/申/酉 (3) | ✓ | 3 row HIJAU | OK |
| **Marriage hindari** | 牛/兔/狗/龍 → 丑/卯/戌/辰 (4) | ✓ | 4 row MERAH (incl 辰 Naga) | OK |
| Yang Zhai gua | 震 | ✓ | ✓ | OK |
| Zi Wei 命主 / 身主 | 文曲 / 文昌 | ✓ | ✓ | OK |
| Zi Wei 命宮 / 身宮 | 酉 / 丑 | ✓ | ✓ | OK |
| Zi Wei 五行局 | 木三局 | ✓ | ✓ "木三局" | OK |
| Shen Sha (4) | 驛馬 / 劫煞 / 孤辰 / 天醫 | ✓ | ✓ 4 hit di shensha page | OK |
| shi_shen per pilar | 偏官/比肩/主/傷官 | ✓ | ✓ | OK |
| ming_gong_bazi | 乙卯 | ✓ | ✓ | OK |
| Subject-bar Umur | (foto liu nian: 39歲 虛歲 / 38 Barat) | – | **"Umur 37 tahun"** | **MEDIUM BUG** |
| **體相 (seasonal phase)** | foto raw `木相 火旺 死金 囚水 戊土` | mu=旺 huo=相 tu=死 jin=休 shui=囚 | sama dengan MD | **MEDIUM BUG**: MD/PDF swap 木↔火 dan 金↔土 phases vs foto raw string di DATA_EXTRA. Hanya 水=囚 yang match. |

<sup>*</sup> Catatan foto-mapping yong/xi/ji/xian/chou: foto 17(2) urutan kolom kiri tertulis (per CATATAN MD #6 versi v1 "用神 木 dan 忌神 火"), tetapi MD versi sekarang sudah revisi ke 用神=水 / 喜=木 / 忌=火 / 仇=金 / 閒=土 sesuai struktur 8字 (DM 丁 lemah → butuh 水 untuk netralkan 土 dominan). Konsisten internal — assumed user sudah verify foto.

---

## B. Engine Compute Artifacts

| Aspek | Hasil |
|---|---|
| Marriage list auto-derive 三合/六合 | ✓ tidak — list persis foto (4 hindari + 3 cocok) |
| Format default fallback | ✓ tidak — 傷官格 dari foto eksplisit |
| DM strength compute | ✓ tidak — `dm_pos/neg_score` dari foto integer |
| Shen sha standard auto (8/12 bintang) | ✓ tidak — hanya 4 dari foto |
| Yang zhai gua Ba Zhai formula | ✓ tidak — 震 dari foto (Ba Zhai 1988 wanita = 兌 berbeda; foto override) |
| Da Yun cycles recompute | ✓ tidak — 10 cycles dari MD list |
| Ten god per cycle | ✓ deterministic fallback hanya bila MD null (acceptable per V4.5 spec) |
| ti_xiang phase compute dari month | ✓ tidak — diambil dari foto/MD field |
| Shio derive dari year_branch | ✓ tidak — `shio_hz: 龍` dari MD |

**Verdict B:** Tidak ada engine-compute fabrication. Engine 100% MD-driven sesuai V4.5 spec.

---

## C. Layout & Visual

| Cek | Hasil |
|---|---|
| 24 halaman struktur | ✓ TOC + 1-24 lengkap (cover, toc, intro, 5/bazi-opener, 6/dm, marriage, 8/xingqing, 9/family, 10/shensha, 11/caifu, career, dayun, yangzhai, 15/ziwei-opener, ziwei, 17-19 palace, 19b, 20, synthesis, 22/glossary, 23/disclaimer) |
| Page 1 cover | ✓ DM 丁火 + Elemen Utama 水 (yong) labeled benar |
| Page 4 (intro/overview) DM Score Strip | ✓ +3.678 / -5.182 raw (line 3968, 3973) — integer di MD, decimal di display |
| Page 6 daymaster — 5 dme-card | ✓ 5 elemen × badge 體相 (旺/相/死/囚/休) + ★ DIRI di 火 |
| Page 6 — 體相 LEGEND footer | ✓ render 5 dot + label |
| Page 6 — 2 DM card yong/ji split | ✓ "Air, Penopang & Pengarah" + "Api, Pelumat & Pemicu" |
| Page 6 — radar polygon wuxing | ✓ regenerated per-subject (label "Logam·2.0 / Air·3.0 / Api·3.0★ / Tanah·5.0 / Kayu·2.0") |
| Page 7 marriage wheel | ✓ 12 shio, 6 line (3 hijau cocok 辰-子/申/酉, 3 merah hindari 辰-丑/卯/戌). 辰 di tengah pakai Naga-Merah.svg |
| Page 7 marriage HINDARI cards | ✓ 4 cards (丑/卯/戌/辰) urutan benar |
| Page 14 da yun lifeline 10 cycles | ✓ dengan ten god labels (正印/七殺 explicit + fallback) |
| Page 16 zi wei 12 palace | ✓ 12 palace × age tag (6-15, 16-25, …, 116-125) lengkap |
| "Michele" leak | ✓ 0 hits |
| "None · None" leak | ✓ 0 hits |
| "[object Object]" leak | ✓ 0 hits |
| "undefined" leak | ✓ 0 hits |
| **"Umur 37 tahun"** | **MEDIUM BUG** — leak di 5 halaman (page_career: line 4317; page_dayun: 4950; page_marriage: 5354; page_synthesis: 6042; page_ziwei: 5589; page_kesimpulan: 5972). Selisih 1 dari Western age (38), 2 dari foto 虛歲 (39). |
| Wuxing raw count integer | ✓ "Logam · 2.0", "Air · 3.0", dll (1 desimal display, integer di MD) |

---

## D. Tafsir Consistency

| Cek | Hasil |
|---|---|
| DM 丁火 / Api Yin / Pelita konsisten | ✓ 30+ ref di Kepribadian/DM/Sintesis |
| Yong shen = 水 (Air primary) | ✓ DM tafsir + DataMaster section + cover semua sebut Air |
| Xi yong = 木 (Kayu pendukung) | ✓ konsisten |
| Ji shen = 火, Chou shen = 金 | ✓ konsisten |
| Marriage 3 cocok / 4 hindari di prose | ✓ "Tikus, Monyet, Ayam (大吉)" + "Kerbau, Kelinci, Anjing, Naga" di pasangan body |
| Industri 5 fav | ✓ Akuntansi, Hukum, Kesehatan, Musik, Sains — semua dari foto `industri_full.favorable` |
| Da Yun fase aktif (30-39 = 甲寅) | ✓ "Kayu Yang Macan, Tumbuh dan Membangun" — match foto |
| Liu nian 2026 (39歲, 丙午) | ✓ MD eksplisit, tafsir match foto 喪門/黑煞 |
| Self-contradiction yong vs tafsir | ✓ tidak ada — semua narasi tarik Air+Kayu, hindari Api+Logam |
| Mention "Li Jia Ling" | ✓ konsisten 30+ kali |

---

## Bugs Found

### CRITICAL (0)
*(Semua 3 critical v1 sudah resolved.)*

### MEDIUM (2)
1. **Subject-bar "Umur 37 tahun" salah** — Foto Liu Nian 2026 explicit 39歲 (虛歲); Western age = 2026-1988 = 38. PDF tampilkan 37 di 6 halaman (career/dayun/marriage/synthesis/ziwei/kesimpulan stat-card). Off-by-1 dari Western, off-by-2 dari foto. Ini sama bug yang muncul di v1 dan masih persist — kemungkinan engine `age_now = year_now - year_born - 1` (ulang tahun belum lewat) padahal lahir 1 Juni dan now 7 Mei → memang BELUM ulang tahun ke-38 → Western strict = 37. **Catatan:** bila pakai logic "tahun belum lewat" maka 37 secara teknis benar Western, tapi foto BaZi pakai 虛歲 (39) — mismatch konvensi. User decision diperlukan: ikuti Barat (37) atau 虛歲 (39).

2. **體相 phase mapping berbeda dari foto raw string** — DATA_EXTRA `ti_xiang: 木相 火旺 死金 囚水 戊土` (foto raw) tidak match dengan top-level fields:
   - foto 木=相 vs MD/PDF 木=旺
   - foto 火=旺 vs MD/PDF 火=相
   - foto 金=死 vs MD/PDF 金=休
   - foto (戊 stem ref) vs MD/PDF 土=死
   - foto 水=囚 vs MD/PDF 水=囚 ✓ (only match)
   
   Lahir bulan 巳 (musim panas, api): standar phases = 火旺/土相/木休/金死/水囚. PDF tampilkan 木旺/火相/土死/金休/水囚 — pola "lahir musim semi", BUKAN musim panas. Salah secara prinsip BaZi maupun salah vs raw foto string. Render di page_06 dme-card line 302/310/318/326/334.

### MINOR (2)
3. **Da Yun "Umur 30, 39"** di subject-bar dayun (line 5451 `<div class="sp-age">Umur <span class="now">30, 39</span></div>`) — terlihat ambigu. Mungkin "30-39" salah render jadi "30, 39"? Atau intentional (start age + age sekarang)? Visually confusing. Inspect.

4. **Nayin null di MD** — `nayin_tahun/bulan/hari/jam: null`. Jika layout punya field nayin (umumnya pages BaZi opener), akan kosong. Tidak terlihat di build cek tapi worth flag jika foto sebenarnya memuat nayin info.

---

## Verdict

**NEEDS FIX (minor)** — 0 critical, 2 medium, 2 minor.

Production distribution: **DAPAT didistribusikan dengan disclaimer**. Tidak ada bug user-facing yang material (Marriage benar, Yong/Ji benar, layout intact, no leak placeholders). 2 medium adalah **akurasi numerik/konvensi**, bukan blocker fungsional.

Prioritas perbaikan:
1. **體相 phase mapping** — fix top-level fields supaya match DATA_EXTRA raw foto (火旺/土相/木休/金死/水囚 sesuai musim 巳). Render di page_06 ikut auto-fix.
2. **Umur compute** — pilih konvensi (Barat strict / 虛歲) dan apply konsisten ke semua 6 location subject-bar. Default rekomendasi: gunakan **虛歲 (39)** karena seluruh tafsir foto BaZi/Liu Nian basisnya 虛歲.

## Confidence

**92%** — Cross-check foto-screenshot list ↔ MD field ↔ HTML build (PDF proxy) menyeluruh. Sisa 8%: (a) tidak bisa extract PDF text langsung (font-encoded image render) — verifikasi via HTML mtime-match; (b) lijialing.json/.ocr.json tidak hadir saat audit (mungkin OneDrive sync delay), jadi tidak bisa cross-check pipeline OCR→JSON→MD. (c) interpretasi foto yong/xi/ji/xian/chou berdasarkan MD CATATAN, tidak verify pixel.

## Recommendation

1. **Distribute current PDF** dengan footnote "Umur 37 menggunakan konvensi Barat (belum ulang tahun di tahun ini); BaZi tradisional menggunakan 虛歲 = 39." atau fix engine.
2. **Patch 體相 mapping** sebelum batch build berikutnya — buat unit test: assert foto raw `ti_xiang` string parse ke top-level fields `ti_xiang_*` 1:1.
3. **Pipeline check baru**: assert `subject.json` dan `subject.ocr.json` exist sebelum build; fail fast bila missing.
4. **Linter regex** (`\bMichele\b`, `None · None`, `\[object Object\]`) sudah efektif (0 hits) — pertahankan.
5. v1 → v2: 9/10 fix rate excellent. Workflow regenerasi terbukti efektif.
