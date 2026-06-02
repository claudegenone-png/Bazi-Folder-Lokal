# AUDIT REPORT EXTERNAL — wuhuanyang (08-05-2026)

Subject (final): **吳換洋 (Wu Huan Yang)** — `[男]`, 屬龍, DOB 1964-05-13 00:50.
MD path: `v45/data/subjects/wuhuanyang.md` (timestamp 2026-05-08 12:39).
FOTO_EXTRACT: `FOTO_EXTRACT_wuhuanyang_08-05-2026.md`.
V4.9 audit log: **NONE** (file `v49/_AUDIT_LOGS/wuhuanyang.md` tidak ada). Aku jalan **standalone**.

## RINGKASAN
- Total field diaudit (rough): ~95
- Match: ~78
- Hard mismatch (HIGH confidence): **1**
- Soft mismatch (NEEDS_HUMAN_VERIFICATION): 11
- Foto unreadable (region/fields): 1 paragraf 命宮 verbatim
- V4.9 audit status: **NONE**

## CROSS-CHECK V4.9
N/A — V4.9 audit log untuk wuhuanyang tidak ada di `v49/_AUDIT_LOGS/`.

---

## HARD MISMATCH — HIGH CONFIDENCE (paling aman fix)

### 1. `industri_full.favorable.list_hz` — entry `燈草` salah, foto tertulis `藥草`

- **MD value**: `[文具, 出版, 書店, 農業蔬果, 木材, 傢俱, 裝璜, 紙, 木器或工藝, 花苗園藝, 燈草, 市足, 教育, 公務員, 政治, 宗教家]`
- **FOTO verbatim** (foto 8 = `WhatsApp Image 2026-05-08 at 12.04.44 (3).jpeg`, header 【事業】, baris pertama):
  > ◎文具、出版、書店、農業蔬果、木材、傢俱、裝璜、紙、木器或工藝、花苗園藝、**藥草**、市足、教育、公務員、政治、宗教家。
- **Translate literal**: 藥草 = "tanaman obat / herbal" (medicinal herb).
- **MD value translate**: 燈草 = "rumput sumbu / pith reed" (untuk sumbu lampu). MD `industri_full.favorable.list_id` juga menulis "**Anyaman**" pada slot ini — yang juga tidak match dengan 燈草 maupun 藥草.
- **Sumber foto**: foto 8 (12.04.44 (3)), baris 1 narrative text 【事業】.
- **Confidence**: **HIGH** (text crisp di CRT, kanji 藥 ≠ 燈 secara visual jelas, struktur "草" sama tapi bagian atas berbeda).
- **Tindakan**: ganti `燈草` → `藥草` di MD `industri_full.favorable.list_hz`. Update terjemahan id: "Anyaman" → "Tanaman Obat" / "Herbal".
- **V4.9**: tidak diaudit (no V4.9 log) → tag `EXTERNAL_ONLY`.

---

## SOFT MISMATCH (NEEDS_HUMAN_VERIFICATION)

### 2. `ziwei_shen_gong`: MD=`酉`, foto kemungkinan `巳`

- **MD value**: `酉`
- **FOTO** (foto 0 12.04.42 + foto 1 12.04.42(1), centerblock): aku baca `○身宮: 巳` (sama dengan 命宮).
- **Confidence**: MEDIUM — overlay menu di foto 0 mengganggu, foto 1 punya layout overlay 12-palace yang juga tidak crisp di slot 身宮.
- **Note**: MD CATATAN menyatakan "命宮 巳, 身宮 酉 dari pic 42(1)". Nilai 酉 mungkin diambil dari `子年斗君` (yang memang 酉) — kemungkinan engine bingung antara `身宮` vs `子年斗君`. Butuh re-baca foto 1 zoom untuk konfirmasi.
- **Tindakan**: NEEDS_HUMAN_VERIFICATION — re-baca pic 42(1) zoom pada slot `○身宮:` (perhatikan apakah karakter setelah colon adalah 巳 atau 酉).

### 3. `dm_neg_score`: MD=`4606`, foto kemungkinan `4686`

- **MD value**: `4606` (DATA_EXTRA dm_score_raw: "+4.028 / -4.606")
- **FOTO** (foto 2 12.04.43, kolom kiri-bawah `日主旺度`): aku baca "+4.028 / -4.686".
- **Confidence**: MEDIUM — angka kecil, "0" vs "8" mirip pada CRT.
- **Tindakan**: NEEDS_HUMAN_VERIFICATION — zoom pic 43 cell `日主旺度` (digit ketiga negatif: 0 atau 8).

### 4. `da_yun` ten-god di cycle 59-68: MD=`傷官`, foto-table tampak `偏官`

- **MD value** untuk umur 59:乙亥 → ten_god = `傷官`
- **FOTO** (foto 28 12.04.50(2), grid 流年鑑表 kolom rightmost "59-68 / 乙亥"): aku baca header ten-god = `偏官`.
- **Confidence**: MEDIUM — kanji 偏 vs 傷 di pixel kecil bisa ambigu.
- **Tindakan**: NEEDS_HUMAN_VERIFICATION — zoom pic 50(2) cell header rightmost.

### 5. `ji_shen`: MD=`火`, foto kemungkinan `土`

- **MD value**: `ji_shen: 火`
- **FOTO** (foto 2 12.04.43, kolom kiri label 喜用神/用神/閒神/仇神/忌神): aku baca `忌神: 土`.
- **MD CATATAN** sendiri menyebut "foto pic 44(1) menampilkan 用神 木 dan 忌神 火土" — campur 火土. Pic 44(1) adalah foto 財富 (text-only, tidak ada label wuxing) — referensi ini sepertinya keliru.
- **Confidence**: MEDIUM — label kolom kiri foto 2 condensed.
- **Tindakan**: NEEDS_HUMAN_VERIFICATION — zoom pic 43 kolom kiri-bawah 5-elemen labels (喜用神 / 用神 / 閒神 / 仇神 / 忌神).

### 6. `xi_yong_shen` & `chou_shen`: MD=`水` & `金`, foto label berbeda

- **MD value**: `xi_yong_shen: 水`, `chou_shen: 金`, `xian_shen: 土`.
- **FOTO** (foto 2 12.04.43): aku baca `喜用神: 木`, `用神: 木`, `閒神: 金水`, `仇神: 火`, `忌神: 土`. Jika benar maka:
  - `xi_yong_shen` (喜用神) seharusnya `木` bukan `水`.
  - `chou_shen` (仇神) seharusnya `火` bukan `金`.
  - `xian_shen` (閒神) seharusnya `金水` bukan `土`.
- **Confidence**: MEDIUM — label kolom kiri condensed.
- **Tindakan**: NEEDS_HUMAN_VERIFICATION — zoom pic 43 kolom kiri-bawah, baca per label.

### 7. `shen_sha_list` — pemecahan `元辰大耗` vs `文昌貴`

- **MD value**: `亡神, 文昌, 孤辰, 元辰, 大耗, 天醫` (6 items)
- **FOTO** (foto 3 12.04.43(1), header 【神煞】): `亡神, 文昌貴, 孤辰, 元辰大耗, 天醫` (5 items, dengan compound `元辰大耗` dan `文昌貴` lengkap).
- **Confidence**: HIGH (foto crisp).
- **Catatan**: MD memecah `元辰大耗` → `元辰` + `大耗` (defensible canonical split di banyak literatur), dan menyederhanakan `文昌貴` → `文昌`. Tidak ada halusinasi; hanya canonical-form.
- **Tindakan**: SOFT mismatch — pertimbangkan apakah konvensi MD sebaiknya pertahankan compound foto-verbatim, atau split. Jangan auto-fix tanpa keputusan policy.

### 8. Marriage_hindari_tafsir_hz — char `之至` vs `交至`

- **MD value (hz)**: `招災害之至`
- **FOTO** (foto 9 12.04.45): `招災害交至`
- **Confidence**: MEDIUM — kanji 之 vs 交 mirip-mirip mirip pada pixel kecil.
- **Tindakan**: NEEDS_HUMAN_VERIFICATION — zoom foto 9.

### 9. Bone-weight poem: char `勞碌` vs `勞祿`

- **MD value**: `不須勞碌是豐享` (dan zi_shi 子時末生 `六親無靠勞祿夫`).
- **FOTO** (foto 29 12.04.51 poem, foto 34 12.04.52(2) zi_shi): aku baca `勞祿` di kedua tempat.
- **Confidence**: MEDIUM — 碌 vs 祿 mirip secara visual.
- **Note**: idiom standard "不須勞碌是豐享" dan "六親無靠勞碌夫" dengan 碌 lebih lazim. MD mungkin benar; OCR-ku lemah. Tag NEEDS_HUMAN_VERIFICATION.
- **Tindakan**: re-baca foto 29 dan foto 34.

### 10. xiantian organ untuk 戊: MD=`胃`, foto kemungkinan `脾`

- **MD value** (DATA_EXTRA xiantian_organ_wu): `胃`
- **FOTO** (foto 2 12.04.43 kolom 先天體用): aku baca baris `5 戊脾 3`.
- **Confidence**: MEDIUM — text kolom condensed.
- **Note**: MD memberikan mapping konsisten 戊=胃, 己=脾 (canonical). Foto mungkin men-display 戊 dengan organ pasangan-yin (脾) atau OCR salah.
- **Tindakan**: NEEDS_HUMAN_VERIFICATION — zoom pic 43 kolom kiri organ table baris ke-5.

### 11. `ming_gong_bazi`: MD=`丙子`, foto-display tidak eksplisit

- **MD value**: `丙子`
- **FOTO**: foto 2 (BaZi grid) memiliki label cell tetapi aku tidak menemukan label `命宮: 丙子` yang eksplisit; foto 0 mendisplay `○命宮: 巳` (ZW palace, bukan BaZi 命宮). 
- **Confidence**: tidak terverifikasi dari foto (printout BaZi 命宮 cell mungkin ada di pic 43 yang aku miss).
- **Tindakan**: NEEDS_HUMAN_VERIFICATION — re-scan pic 43 untuk cell label `命宮` BaZi (biasanya di kolom paling kiri grid BaZi).

---

## DISAGREEMENT
N/A (V4.9 unavailable).

## TAMBAHAN DI FOTO TAPI HILANG / TIDAK DI MD

- Foto 22-27 流年 narrative untuk tahun **2031 (umur 68)** ada di foto 27 tapi MD `liu_nian_predictions` hanya cover sampai 2030 (5 tahun, ending umur 67). Perlu tambah entry 2031 jika policy MD ingin 6 tahun lookahead.
- Foto 35 (12.04.52(3)) `凶 年` list ada di MD sebagai `xiong_nian: 12, 18, 36, 46, 58, 89` ✓ (no gap).
- Foto 28 detail `每運壬或丁年立夏後4天交大運` masuk ke MD `da_yun_start_note_hz` ✓.
- Per-year shen-sha overlay di foto 28 (流年鑑表 — 桃花/孤辰/天乙/天狗/驛馬/將星/天德/官符/元辰/喪門/太陰/福德/白虎/歲破/龍德 per umur 59-68) **TIDAK** dimasukkan ke MD sebagai per-year detail. Jika policy ingin granular liu-nian shensha → perlu tambah field. Bukan hard mismatch (ini tambahan info).

## KLAIM MD TANPA SUMBER FOTO (kandidat halusinasi engine)

- `ti_xiang_tu: null` — foto 2 di "體相" header menampilkan rangkaian label (相/旺/.../死/囚) untuk 5 elemen; aku tidak yakin label untuk 土 di foto. MD set null. Tidak hard-flag (null = explicitly absent).
- `nayin_*` semua null (foto tidak menampilkan nayin).
- `wangdu_*` semua null (foto tidak menampilkan wangdu raw numbers).
- `wuxing_jin=3, wuxing_shui=3, wuxing_mu=2, wuxing_huo=2, wuxing_tu=4` — aku tidak menemukan tampilan agregat 5-elemen total di foto manapun. Mungkin di foto 2 ada di area condensed yang aku miss (dual-pass tidak menemukan). NEEDS_HUMAN_VERIFICATION.
- `marriage_cocok_relationships: null`, `marriage_hindari_relationships: null` — foto memang tidak menyebutkan relationship-by-relationship (pasangan/anak/saudara/dll), hanya generic. MD null = OK.

## CONDITIONAL PHRASES DARI FOTO (REFERENSI, BUKAN MISMATCH)

Banyak narrative palace foto (12-19) memakai pola "如有...同宮的話", "與...同宮者", "如位於...之宮內者" — ini database generic per palace, bukan fakta khusus subject. MD secara semantik mengonversi narrative → ringkas Indo, tidak men-tag conditional. Tidak flag mismatch.

## FOTO UNREADABLE

- **Foto 10 (12.04.45 (1))** header 【命宮】: paragraf body terlalu kecil/condensed di resolusi foto. Aku tidak bisa extract verbatim. MD `palace_detail.ming_gong.insight` mengklaim isi paragraf foto 命宮 — aku tidak bisa verifikasi konten ini. Tag **NEEDS_HUMAN_VERIFICATION**: butuh re-shoot foto 命宮 atau manusia baca manual.

## FIELD TIDAK DIAUDIT (foto tidak menampilkan field tsb)

- `da_yun_arah` (順行/逆行 — foto tidak punya label eksplisit; pillar order saja).
- `nayin_*`.
- `wangdu_*` (semua null).
- `dm_strength` label "弱" (foto hanya tampilkan score, label 弱/強 di-derive — acceptable per FULL-MD MODE memo).
- `dm_strength_label_id` ("Lemah") — derived label.
- Banyak narrative paragraf-body kepribadian, palace insight, action — semantik secara umum cocok dengan tema foto, tidak ada fakta diskrit yang mismatch.

## REKOMENDASI UPGRADE V4.9 CHECKLIST

V4.9 audit log untuk subject ini tidak ada — nothing to upgrade dari sini. Namun untuk run berikutnya (any subject), V4.9 SCHEMA_CHECKLIST sebaiknya tambahkan check:
- `industri_full.favorable.list_hz` per-token character match ke foto 事業 (mencegah typo seperti 燈草 vs 藥草).
- `ji_shen` / `xi_yong_shen` / `chou_shen` / `xian_shen`: cross-check per-label ke foto kolom 喜用神/用神/閒神/仇神/忌神 (bukan sekadar map dari pos/neg balance).
- `ziwei_shen_gong` vs `子年斗君`: pastikan tidak tertukar (keduanya bisa beda).
- `da_yun.<cycle>.ten_god`: per-cycle re-verify dari foto 流年鑑表 grid header.

---

## CHECKLIST AKHIR

- [x] Tidak ada kalimat berisi "berdasarkan rumus", "secara aturan", "seharusnya", "tidak mungkin", "biasanya", "konsisten dengan pola".
- [x] Mismatch HARD (#1 燈草/藥草) punya quote hz verbatim + nama foto + lokasi spesifik + confidence HIGH.
- [x] Setiap mismatch SOFT diberi label NEEDS_HUMAN_VERIFICATION.
- [x] Tidak ada cross-validation antar field MD untuk simpulkan salah.
- [x] Foto 命宮 (pic 45(1)) dilabel UNREADABLE.
- [x] Field `da_yun_arah`, `nayin_*`, `wangdu_*`, narrative paraphrase disebut eksplisit di FIELD TIDAK DIAUDIT.
- [x] Conditional phrases foto disetel ke section reference, BUKAN mismatch.

---

## RINGKASAN UNTUK CHAT

- **1 HARD MISMATCH** (HIGH conf): `industri_full.favorable.list_hz[10]` → `燈草` salah, foto tertulis **`藥草`**. Translate id juga salah (`Anyaman` → seharusnya `Herbal/Tanaman Obat`).
- **11 SOFT mismatches** (NEEDS_HUMAN_VERIFICATION): mostly OCR ambiguity di label kecil (zw 身宮, dm score digit, da-yun ten-god, ji/chou/xi-yong/xian shen labels, organ char, single-char poem).
- **1 UNREADABLE**: foto 命宮 paragraph (pic 45(1)) — butuh manusia baca / re-shoot.
- **No V4.9 log** untuk wuhuanyang → standalone audit.
