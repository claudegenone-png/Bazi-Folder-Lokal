# Validation Report — Li Jia Ling 李佳玲 (1988-06-01 15:00)

**Agent:** V (PDF Validator) · **Mode:** V4.5 Full-MD · **Date:** 2026-05-07
**Source PDF:** `C:/Users/sukam/OneDrive/Documents/Ramalan/#result/2026-05-07/Li Jia Ling-李佳玲-1988-06-01.pdf` (24 pages)
**Build dir:** `C:/Users/sukam/OneDrive/Documents/Ramalan/v45/_build/lijialing/`

---

## Photo Inventory (28 WhatsApp jpegs)

| Filename suffix | Screen | Notes |
|---|---|---|
| 10.51.17 | 全局總論 | Pasangan reputasi baik, anak ekspresif, ibu tegas, keras kepala |
| 10.51.17 (1) | 財富 (BaZi) | 偏財 普通, 正財 豐厚 — 投機性vs投資性 |
| 10.51.17 (2) | **COVER (main BaZi)** | grid 戊辰丁巳丁亥戊申, 用神水/喜神金/閒神土/仇神木/忌神火, 用事卦格 傷官, +3.678 / -5.182 |
| 10.51.18 | (Zi Wei chart full grid - alt thumb) | 12 palace overview |
| 10.51.18 (1) | **Zi Wei 命盤** | 命主 文曲, 身主 文昌, 命宮 酉, 身宮 丑, 木三局, 子年斗君 巳 |
| 10.51.18 (2) | **神煞** | 驛馬, 劫煞, 孤辰, 天醫 (4 stars only) |
| 10.51.18 (3) | **性情** | religious, ramah, peduli, peka wajah, hormat keputusan kelompok |
| 10.51.19 | **陽宅** | 震卦 — 坐北向南/南向北, 門 南北東南, 爐 西方, 床 東方 |
| 10.51.19 (1) | **事業** | 鋼鐵/五金/採礦/汽車/機械/科學家/律師/會計/金融 etc |
| 10.51.19 (2) | **婚配** | 忌: **配相牛、兔、狗、龍** (4 items: 丑卯戌辰); 宜: 鼠、猴、雞 |
| 10.51.20 | 命宮 (Zi Wei detail) | tegas + luwes seimbang |
| 10.51.20 (1) | 夫妻 | 平穩順利, tidak火熱戀情 |
| 10.51.20 (2) | 財帛 | 不賭博, 巨門星致富, 天梁星策略 |
| 10.51.21 | 疾厄 | 消化器官, 脊髓, 皮膚, 痔瘡 |
| 10.51.21 (1) | 遷移 | 意外情況, 旅行轉業搬家 |
| 10.51.21 (2) | 僕役 | 寅午戌方位 hati-hati |
| 10.51.22 | 官祿 | 武曲, 教師/公務員/科學家/技術 |
| 10.51.22 (1) | 田宅 | 寅卯巳午 warisan, 水邊大吉 |
| 10.51.22 (2) | 福德 | 太陰, 享福延年 |
| 10.51.23 | 父母 | 個性穩重, 經濟富裕, 紫微/武曲 hangat |
| 10.51.23 (1) | 古書云 | 三命通會註, 滴天髓 詩云 |
| 10.51.23 (2) | **流年 2026** (民國115, 39歲, 丙午) | 喪門, 黑煞 |
| 10.51.23 (3) | 流年 2027 (40歲, 丁未) | 太陰, 文昌 |
| 10.51.24 | 流年 2028 (41歲, 戊申) | 官符, 火煞 |
| 10.51.24 (1) | 流年 2029 (42歲, 己酉) | 死符, 暗燿 |
| 10.51.24 (2) | 流年 2030 (43歲, 庚戌) | 歲破, 太陰 |
| 10.51.25 | 流年 table 30-39 | 30-39 大運 甲寅 |
| 10.51.25 (1) | 流年 table 40-49 | 40-49 大運 癸丑 |

---

## A. Data Integrity (foto ↔ MD ↔ JSON ↔ PDF)

| Field | Foto (truth) | MD | JSON | PDF | Status |
|---|---|---|---|---|---|
| Nama | 李佳玲 Li Jia Ling | ✓ | ✓ | ✓ | OK |
| Gender | 女 (陽女 di Zi Wei) | Wanita | 陰女 | Wanita | **MEDIUM**: JSON menulis 陰女 padahal Zi Wei chart tertulis 陽女 |
| Lahir | 1988-06-01 15:00 | ✓ | ✓ | 1 Juni 1988 · 15:00 | OK |
| Pillars | 戊辰/丁巳/丁亥/戊申 | ✓ | ✓ | ✓ | OK |
| Wuxing | 金2 水3 木1 火2 土5 | ✓ | ✓ | ✓ (label text) | OK |
| **Format (卦格)** | **傷官 (用事卦格 傷官, 用事 傷官)** terbaca jelas | null | – | tidak ditampilkan | **CRITICAL**: Foto eksplisit menulis 傷官, MD/JSON kosong → tafsir Sintesis hanya menyebut "傷官 dominan" tanpa label format resmi |
| **Yong Shen** | **水** (cover bottom-left: 用神 水) | 木 火 | 木 火 | 木 火 (label di Sintesis) | **CRITICAL**: Foto menulis 用神=水, MD pakai 木火 (lihat CATATAN #6 — autor MD admit ambigu, dipilih konvensional). Output PDF KONTRADIKTIF dengan foto |
| **Ji Shen** | **火** (cover: 忌神 火) | 土 水 | 土 水 | 土 水 | **CRITICAL**: Foto 忌神=火 (Api), MD menulis 土 水 — secara fundamental beda mapping. Tafsir bahkan menyebut "Api Yin pelita, ditambah Kayu" sebagai yong, padahal foto bilang Air |
| Xi Shen | 金 | null (DATA_EXTRA xi_shen=null) | – | – | **MEDIUM**: foto eksplisit 喜神 金, MD biarkan null |
| Xian Shen | 土 | null | – | – | MINOR |
| Chou Shen | 木 | null | – | – | MINOR |
| DM strength | +3.678 / -5.182 → 弱 | ✓ | ✓ | ✓ "LEMAH" | OK |
| Da Yun cycles | 10/20/.../100, 丙辰→丁未 (10 cycles) | ✓ | ✓ | ✓ | OK |
| Da Yun arah | 逆行 (foto: stem 丙→乙→甲 mundur) | 逆行 | "backward" | rendered | OK |
| Da Yun start_age | 10 (foto: 8或11個小月滿又後27天) | 10 | 10 | 10 | OK |
| **Marriage 宜** | 鼠、猴、雞 (3) → 子申酉 | 子申酉 | 子申酉 | 子申酉 ✓ | OK |
| **Marriage 忌** | **牛、兔、狗、龍 (4) → 丑卯戌辰** | 丑卯戌辰 ✓ | 丑卯戌 (3 only) ✗ | 丑卯戌 (3 only) ✗ | **CRITICAL**: 龍/辰 hilang di JSON dan PDF. PDF wheel render 辰 sebagai neutral, harus merah (HINDARI). MD benar |
| Yang Zhai gua | 震 | ✓ | ✓ | rendered | OK |
| Yang Zhai door | 南/北/東南 | ✓ | – | rendered | OK |
| Yang Zhai stove | 西方 | ✓ | – | rendered | OK |
| Yang Zhai bed | 東方 | ✓ | – | rendered | OK |
| Zi Wei ming_zhu | 文曲 | ✓ | ✓ | ✓ | OK |
| Zi Wei shen_zhu | 文昌 | ✓ | ✓ | ✓ | OK |
| Zi Wei 命宮 | 酉 | ✓ | ✓ | ✓ | OK |
| Zi Wei 身宮 | 丑 | ✓ | ✓ | ✓ | OK |
| Zi Wei wu_xing_ju | 木三局 | ✓ | ✓ | ✓ | OK |
| Zi Wei 子年斗君 | 巳 | ✓ | ✓ | – | OK |
| Shen Sha list | 驛馬, 劫煞, 孤辰, 天醫 (4) | ✓ | ✓ | rendered | OK |
| Liu Nian 2026 age | **39歲** (foto eksplisit) | usia 39 ✓ | – | – | OK in MD |
| **Subject-bar age** | – | – | – | "Umur 37 tahun" | **MEDIUM**: PDF tampilkan 37, semestinya 38 (Western, lahir 1988→2026) atau 39 (虛歲 ala foto). 37 salah dua-duanya. Bocor di 6 halaman: career, dayun, marriage, synthesis, ziwei, master |
| Zi Wei 12 palace stars (per palace, lengkap) | dari 10.51.18(1) | DATA_EXTRA terisi | – | rendered | OK (cross-check sample: 命宮 紫微/廉貞/鈴星/擎羊 ✓; 福德 太陰 ✓; 官祿 武曲/天相 ✓) |

---

## B. No Engine Compute Artifacts

| Aspek | Hasil |
|---|---|
| Marriage list auto 三合 | ✗ TIDAK auto-derived. Mengikuti foto (kecuali bug missing 辰 yang justru OPPOSITE — list di-trim, bukan di-auto-extend). Status: list lebih PENDEK dari foto, bukan engine compute |
| Format default 正官格 | ✗ Tidak default. Format dibiarkan null (padahal foto eksplisit 傷官) — under-population, bukan auto-default |
| DM strength compute | ✓ Mengambil dari foto (+3678/-5182 → 弱) bukan kompute internal |
| Shen sha 8 standar auto | ✓ Hanya 4 bintang (foto) dipakai, tidak menambahkan 桃花/天乙/天德 standar |
| Yang zhai gua Ba Zhai formula | ✓ Mengambil dari foto (震), tidak kompute dari tahun lahir (1988 wanita = 兌 menurut Ba Zhai, bukan 震) |
| Da Yun arah/start_age compute | ✓ Mengambil dari foto |

**Verdict B:** Tidak ada engine-compute artifact. Semua deviasi adalah **under-population** (data di foto tidak diteruskan ke output), bukan **over-fabrication**.

---

## C. Layout & Visual

| Cek | Hasil |
|---|---|
| 24 halaman | ✓ TOC + struktur 1-24 lengkap (cover, toc, intro, 5/bazi-opener, 6/dm, 7/marriage, 8/xingqing, 9/family, 10/shensha, 11/caifu, career, dayun, yangzhai, 15/ziwei-opener, ziwei, 17-19 palace, 19b/penutup, 20/kesimpulan, synthesis, 22/glossary, 23/disclaimer) |
| Radar polygon DM | ✓ Polygon coordinates konsisten dengan wuxing values 金2 水3 火2 土5 木1 (komentar HTML "Michele's polygon, 金 0.7 ..." adalah komentar STALE, polygon sebenarnya regenerated). MINOR doc-comment leak |
| Wuxing bar | ✓ 5 kartu, value benar |
| Marriage wheel | **CRITICAL BUG**: 辰 Naga rendered sebagai badge neutral (#F5EBD0 grey, opacity 0.6), seharusnya HINDARI (merah, sesuai foto) |
| Da Yun lifeline | ✓ 10 cycles render |
| Shensha grid 8 cards | ✓ (4 active + slot kosong sesuai V4.5 null-safety) |
| Ziwei 12 palace | ✓ render lengkap, tag "Umur 36-45" untuk 大運 fase aktif |
| **"Michele" leak** | **MEDIUM**: HTML comment line 202 "Michele's polygon" + line 4003 di _master.html. Hanya komentar, tidak tampak di PDF render. Tetap perlu dibersihkan |
| **"None" leak** | **CRITICAL BUG**: 6 string literal "None · None" muncul di marriage cards (Tikus/Monyet/Ayam/Kerbau/Kelinci/Anjing tag) — ini adalah Python `str(None)` bocor langsung ke template render |
| **"[object Object]" leak** | ✓ Tidak ditemukan |
| **Subject age leak** | **MEDIUM**: "Umur 37 tahun" di 5 halaman (career/dayun/marriage/synthesis/ziwei) salah; harus 38 (Western) atau 39 (虛歲, sesuai foto liu nian) |

---

## D. Tafsir Consistency

| Cek | Hasil |
|---|---|
| DM 丁火 / Api Yin disebut konsisten | ✓ "Api Yin", "丁火", "pelita" konsisten di Kepribadian/Sintesis/DM section |
| Format claim | ✗ Tafsir Sintesis menyebut "Peta dengan 傷官 dominan" (stats.format_desc) PADAHAL field MD `format = null`. Tafsir berasumsi 傷官 padahal label resmi tidak diisi. Inconsistency soft, tapi tafsir benar (foto memang 傷官) — yang salah adalah field `format` |
| Self-contradictions yong/ji | ✗ Tafsir konsisten internal (Kayu+Api yong, Tanah+Air ji) — tapi BERTENTANGAN dengan foto cover (foto: yong=水, ji=火). Seluruh narasi "tarik Kayu membantu Api" akan SALAH bila foto adalah ground truth |
| Mention "Li Jia Ling" | ✓ Disebut 30+ kali di tafsir, konsisten |
| Da Yun fase aktif | ✓ Usia 30-39 = 甲寅 (foto match), tafsir "Kayu Yang Macan" tepat |
| Liu nian 2026 selaras | ✓ MD bilang "tahun usia 39 丙午, 喪門 masuk" — match foto |
| Pasangan tafsir | ✓ Sesuai 全局總論 photo (konservatif, rasional, sulit direstui ortu) |

---

## Bugs Found

### CRITICAL (3)
1. **Marriage hindari list missing 辰/龍 (Naga)** — Foto eksplisit 4 shio (牛兔狗龍), JSON+PDF hanya 3 (丑卯戌). PDF marriage wheel render 辰 sebagai neutral grey, semestinya merah HINDARI. Bug di OCR atau parser foto. MD sudah benar (4 items) — divergence terjadi di pipeline JSON build.
2. **"None · None" placeholder leak di Marriage cards** — 6 baris menampilkan literal string "None · None" pada tag area shio Tikus/Monyet/Ayam/Kerbau/Kelinci/Anjing. Ini Python `str(None)` bocor ke template Jinja/render. User-facing, sangat terlihat di PDF.
3. **Yong Shen / Ji Shen kontradiksi foto** — Foto cover bottom-left tertulis 用神=水, 喜神=金, 閒神=土, 仇神=木, 忌神=火. MD/JSON/PDF menggunakan yong=木火, ji=土水 (CATATAN #6 admit ambigu, dipilih konvensional). Ini melanggar V4.5 full-MD rule "yong dari foto, jangan derive". Seluruh strategi tafsir (aktifkan Kayu, hindari Tanah) jadi terbalik bila foto ground truth.

### MEDIUM (4)
4. **Format 卦格 tidak diisi padahal foto eksplisit 傷官** — Cover photo jelas tertulis "用事卦格 傷官" dan "用事 傷官". MD set null, PDF tidak menampilkan label format. Tafsir Sintesis tetap menebak "傷官 dominan" — kebetulan benar tapi seharusnya field `format` diisi 傷官格.
5. **Subject-bar age "Umur 37 tahun"** — Salah. 1988 → 2026 = 38 (Western) atau 39 (虛歲, foto). 37 keliru di 5 halaman: career, dayun, marriage, synthesis, ziwei.
6. **Gender code mismatch JSON vs Foto** — Zi Wei chart photo (10.51.18(1)) menunjukkan "陽女" di kanan-atas, JSON `gender_hz: "陰女"`. Wanita lahir tahun 戊辰 (1988, tahun Yang) memang 陽女. Ini kemungkinan typo OCR/parser.
7. **xi_shen / chou_shen / xian_shen null** — Foto memberi mapping lengkap (喜神金, 閒神土, 仇神木) tapi DATA_EXTRA biarkan null. Under-population.

### MINOR (3)
8. **HTML comment "Michele's polygon" stale** — Line 202 page_06_daymaster.html dan line 4003 _master.html. Polygon coordinates SUDAH benar (regenerated untuk Li), hanya komentar template lama bocor. Tidak tampak di PDF cetak, tapi best-practice cleanup.
9. **Ji-è / Qianyi / Puyi / Zinu / Tianzhai / Fumu — `star: null` di palace detail** — Foto Zi Wei chart sebenarnya memuat per-palace stars (DATA_EXTRA `ziwei_stars_*` sudah lengkap). Field `star` di Palace Detail bisa diisi dari DATA_EXTRA, sayang dilewatkan.
10. **dm_pos_score / dm_neg_score disimpan integer** — Foto: +3.678 / -5.182 (3 desimal). MD pakai integer 3678/5182 (sesuai schema). Tidak salah tapi presisi hilang; OK per CATATAN #3.

---

## Verdict

**NEEDS FIX** — 3 critical bug menghalangi production-ready.

Prioritas perbaikan:
1. Fix OCR/JSON parser untuk marriage_hindari (tambah 辰), regenerate marriage wheel agar 辰 bertanda HINDARI merah.
2. Fix template render `str(None)` → tampilkan "—" atau hide tag bila tafsir per-shio kosong.
3. User verify yong_shen/ji_shen mapping foto (水/火 vs 木火/土水). Bila foto ground truth, **rewrite seluruh seksi** Sintesis "tarik Kayu membantu Api" → "tarik Air mendinginkan Api" (atau biarkan dengan disclaimer eksplisit).

Setelah 3 critical di-fix, MEDIUM dapat diselesaikan dalam patch terpisah; MINOR optional.

## Confidence

**95%** — Cross-check foto vs MD vs HTML build vs PDF telah dilakukan menyeluruh. Sisa 5% ketidakpastian: keterbacaan foto untuk yong/ji shen (font monitor CRT-style hijau/merah; "用神 水" terbaca jelas tapi kemungkinan misread bila ada superscript). User MD author sudah flag CATATAN #6 untuk verifikasi manual.

## Recommendation

1. **DO NOT distribute PDF saat ini.** "None · None" leak terlihat user, marriage Naga hilang adalah error material bagi konsultasi jodoh.
2. Verifikasi visual ulang foto 10.51.17 (2) untuk yong/ji shen — bila benar 用神=水, jalankan re-tafsir Sintesis dan Day Master sections.
3. Tambah pipeline check: assert `len(marriage_hindari) == count(shio_label_in_foto)`, fail build bila mismatch.
4. Tambah linter: scan output HTML untuk pattern `\bNone\b`, `Michele`, `\[object Object\]`, `undefined` — fail build bila ditemukan di non-comment area.
5. Fix age compute: `age = year_now - year_born` (Western) atau eksplisit pakai 虛歲 sesuai konvensi foto. Saat ini tampil 37 tidak konsisten dengan keduanya.
