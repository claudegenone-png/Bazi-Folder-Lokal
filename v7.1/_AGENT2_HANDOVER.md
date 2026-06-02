# Handover dari Agent 2 ke Agent 1

> **Catatan dari user untuk Agent 1:** **JANGAN terima mentah** isi dokumen ini.
> Pelajari dulu — verifikasi di kode (`engines/parse_md.py`, `engines/render.py`, `templates/`),
> bandingkan dengan subjek MD existing (`data/subjects/chelsey.md`, `keiko.md`, `wuhuanyang.md`,
> `liyuanqing.md`), lalu putuskan mana yang masuk ke AUDIT_NOTES.

---

## Konteks

Agent 2 (Claude Code paralel) sudah:
1. Baca semua 28 foto di `C:\Users\sukam\OneDrive\Documents\Ramalan\foto\database\07-05-2026\1\` (subjek 李佳玲, 1988-06-01, wanita).
2. Inspect `WEB_CLAUDE_PROMPT.md` baris-per-baris.
3. Cross-check apa yang foto **tampilkan** vs apa yang prompt **minta diekstrak**.

Hasilnya: 2 temuan utama (di bawah).

---

## TEMUAN 1 — Workflow baru: Claude Code yang baca foto, bukan Claude Web

User sudah menyetujui: **switch full ke Claude Code** untuk extraction. Workflow yang dimau:

```
User: "{path foto} pakai V4.5"
  ↓
Claude Code: prep_photos.py (768px) → cache_check.py → parallel Read batch 10 foto/msg
  ↓ (ekstrak per schema)
Claude Code: tulis ke v45/data/subjects/{name}.md
  ↓
Claude Code: python build_pdf.py {name}
  ↓
PDF di #result/{date}/
```

**Trigger 1-baris user, sisanya otomatis. Target ~3-5 menit untuk subjek baru, <1 menit untuk re-run cached.**

### Implikasi untuk Agent 1

1. **`WEB_CLAUDE_PROMPT.md` perlu di-rework** — sekarang ditulis ke audience "Claude Web user paste-able prompt". Untuk workflow baru, audience-nya = Claude Code agent + engine `parse_md.py`. Konten yang menjelaskan UI Claude Web (mis. "buka claude.ai", "upload semua foto", "copy-paste prompt") tidak relevan.
2. **Pertimbangkan split jadi 2 dokumen:**
   - `MD_SCHEMA.md` — spec field MD yang dibaca `parse_md.py` (ini yang authoritative untuk engine).
   - `EXTRACTION_GUIDE.md` — cara baca foto Xing Qiao (untuk Claude Code agent yang ekstrak: disambiguasi Hanzi, layar mana berisi apa, dst).
3. **Apakah Claude Web tetap didukung paralel?** Saran: deprecate. Schema baru terlalu kaya untuk single-shot Claude Web.
4. **AUTORUN.md** sudah cocok dengan workflow ini (parallel batch Read, cache hash sweep, 1× write ocr.json) — tinggal tambah step "ekstrak ke MD" di Phase 3 untuk Full-MD mode.

---

## TEMUAN 2 — Prompt sekarang under-extract foto

Prompt `WEB_CLAUDE_PROMPT.md` saat ini **memotong / membatasi** banyak informasi yang sebenarnya **eksplisit muncul di foto Xing Qiao**. User mau "100% sumber dari foto, tidak ada interpretasi". Pola yang benar: **ekstrak full di MD (raw + ringkas) → engine pilih budget kata di rendering**, bukan potong di sumber.

### KRITIS — informasi besar yang sama sekali tidak diekstrak

#### 2.1 Layar 古書云 (Classical Quotes) — foto 10.51.23(1)
Foto berisi kutipan literatur klasik **eksplisit untuk subjek**:
- 三命通會註, 滴天髓, 詩曰, 詩云
- Contoh isi: "丁火柔中, 內性昭融, 抱乙而孝, 合壬而忠, 旺而不烈, 衰而不窮, 如有嫡母, 可秋可冬..."

**Tidak ada field di prompt.** Ini sumber tafsir paling tinggi otoritas — wajib diekstrak.

**Saran field:**
```
- gushu_yun_raw: {full hanzi raw dari foto}
- gushu_yun_indo: {ringkasan Indo / penerjemahan, untuk render PDF}
```

#### 2.2 Layar 流年 (Annual Forecast) per tahun — foto 23(2), 23(3), 24, 24(1), 24(2)
6 tahun ke depan (2026-2030+, umur 39-43+) dengan struktur per tahun:
- 西元 / 民國 / 歲次干支 / 歲 (umur)
- Bintang teraktivasi: 太陰, 文昌, 暗曜, 死符, 官符, 喪門, 黑煞, 火殺, 圓滿, 太歲, 歲破 dst — **tiap bintang punya penjelasan 1-2 kalimat**.
- Forecast paragraf umum.

**Prompt sekarang cuma punya note "(Opsional) Layar 流年 — interpretasi tahun sekarang"** tanpa schema. Ini perlu jadi struktur per-tahun lengkap.

**Saran field (list of objects):**
```
- liu_nian:
  - tahun_xy: 2026
    minguo: 115
    sui_ci: 丙午
    umur: 39
    bintang_aktif:
      - {nama: 喪門, deskripsi: "喪門入命求, 孝服有衰災, 刑沖剋害, 破耗又失財"}
      - {nama: 黑煞, deskripsi: "..."}
    prosa_umum: {full text dari foto}
  - tahun_xy: 2027
    ...
```

#### 2.3 Layar 流年 grid 10-tahun per da yun — foto 10.51.25 dan 25(1)
Grid super-padat per cycle da yun. Untuk tiap umur (mis. 30-39 atau 40-49):
- Stem-branch tahun
- Ten god (劫財/偏印/正印/七殺/正官/...)
- Hidden stems + ten god di-cabang
- 12 長生 (病/死/墓/絕/胎/養/長生/沐浴/冠帶/臨官/帝旺/衰)
- 神煞 (將星/亡神/寡宿/桃花/天乙/文昌/天德/紅鸞/羊刃/華蓋)
- 12 太歲神 (太歲/太陽/喪門/太陰/官符/死符/歲破/福德/白虎)

**100% tidak ada di prompt.** Ini "peta tahunan" presisi — bisa dipakai render halaman da yun lebih kaya.

**Saran field:**
```
- liu_nian_grid:
  - umur: 30
    gz: 戊戌
    ten_god: 比肩
    canggan: {...}
    chang_sheng: 長生
    shen_sha: [文昌, 天乙]
    tai_sui_shen: 太陽
  - umur: 31
    ...
```

#### 2.4 Layar 神煞 dengan PENJELASAN per shen sha — foto 10.51.18(2)
Foto bukan cuma list nama shen sha, tapi tiap shen sha punya 1-baris tafsir:
- 驛馬: "勞碌好動、奔波遠行、多旅行運、住家及事業多變動"
- 劫煞: "聰明敏捷、才智過人、巧於謀事"
- 孤辰: "形孤骨露、面無和氣、六親終有也如無"
- 天醫: "在醫界一定成名、為人敬仰、可作良醫"

**Prompt sekarang `shen_sha_list: 天乙貴人@日, 文昌@月, ...`** — buang seluruh tafsirnya.

**Saran field (ganti dari string flat ke list objects):**
```
- shen_sha:
  - nama_hz: 驛馬
    pilar: {kalau ada di foto utama}
    tafsir_raw: {1-2 baris hanzi dari foto}
    tafsir_indo: {terjemahan ringkas}
  - nama_hz: 劫煞
    ...
```

#### 2.5 Main BaZi grid — banyak field hilang dari prompt
Foto 10.51.17(2) + 10.51.18 punya field-field yang **eksplisit muncul** tapi prompt tidak minta:

- **體相** (5-element 旺相休囚死 status): mis. baris atas grid: `木相 / 火相 / 死金 / 因水`. Penting untuk analisis kekuatan elemen.
- **喜神 / 閒神 / 仇神** (3 kategori extra di samping `yong_shen`+`ji_shen` yang sudah ada). Foto ada **5 kategori lengkap**: 喜/用/閒/仇/忌, masing-masing dengan elemen-nya.
- **十神 per pilar** (傷官/比肩/偏官 di atas tiap stem) — full label per pilar.
- **藏干 + 十神 di-cabang** (canggan + ten god labels per hidden stem) — prompt punya `canggan_*` tapi opsional, dan tidak minta ten god label-nya.
- **12 長生 per pilar** (臨官/帝旺/衰/病 dst di bawah branch) — sama sekali tidak ada di prompt.
- **日主旺度 main-grid format** (mis. `+3.678 / -5.182`) — formatnya **berbeda** dari yang di layar 批命備註. Prompt cuma punya `dm_pos_score`/`dm_neg_score` mengacu ke 批命備註.
- **生於 ... 後天交大運** (節氣 / solar term context untuk da yun start) — info kapan mulai da yun secara 24 節氣.
- **空亡 (Kong Wang)** kalau ada di grid — branch yang "kosong".

**Saran field:**
```
- ti_xiang: {體相 5-elemen status, mis. "木相 火相 死金 因水"}
- xi_shen: {喜神 elemen}
- xian_shen: {閒神 elemen}
- chou_shen: {仇神 elemen}
- shi_shen_per_pilar: {tahun: 偏官, bulan: 傷官, hari: 主, jam: 比肩}
- canggan_shi_shen_<pilar>: {ten god untuk tiap hidden stem}
- chang_sheng_<pilar>: {12 長生 phase per pilar}
- kong_wang: {space-emptiness branches kalau ada}
- da_yun_jieqi: {solar-term context, mis. "11年小滿後天交大運"}
- dm_pos_grid_score / dm_neg_grid_score: {pos/neg di main grid, ±X.XXX}
```

#### 2.6 Zi Wei layar — foto 10.51.18(1) — under-captured berat
Tiap dari 12 palace berisi **multi-bintang lengkap**. Contoh palace 田宅:
> `貪狼旺 文截 祿存 天截 養刑空 喪 甲申 將星 白虎`

**Prompt sekarang minta cuma:**
```
- star: {hanzi main star 1-2 karakter}
```

**Buang ~80% data zi wei.** Yang hilang:
- Multi-star list per palace (5-15 bintang)
- 廟/旺/陷 modifier per bintang (kondisi bintang)
- 小限 (current-age range) per palace — angka penting untuk navigasi umur
- 化權 / 化科 / 化祿 / 化忌 transformations: foto eksplisit "○貪狼:化權, ○右弼:化科, ○太陰:化權, ○天機:化忌"
- Bintang sekunder (祿存/天截/將星/白虎/亡龍/神德/福德 dst)

**Saran field:**
```
- ziwei_palaces:
  - nama_palace: 田宅
    branch: 申
    stars:
      - {nama: 貪狼, modifier: 旺}
      - {nama: 文截, modifier: null}
      - {nama: 祿存, modifier: null}
      ...
    secondary_stars: [喪甲申, 將白星虎]
    xiao_xian: "93-102"
- ziwei_transformations:
  - 化權: 貪狼
  - 化科: 右弼
  - 化祿: 太陰
  - 化忌: 天機
```

### SEDANG — sudah ada tapi dibatasi di sumber

#### 2.7 Tafsir per section dipotong di budget kata
Foto 詳細解說 untuk: 全局總論, 性情, 婚配, 事業, 財富, 陽宅, 命宮, 夫妻, 財帛, 疾厄, 遷移, 僕役, 官祿, 田宅, 福德, 父母 — masing-masing 80-150 kata Hanzi.

**Prompt potong jadi 40-55 kata STRICT (body card) atau 60-90 kata (paragraf).** Tafsir asli hilang, tidak bisa di-audit.

**Saran:** simpan **raw Hanzi** di `tafsir_raw_<section>` + ringkasan Indonesia di field tafsir biasa. Engine yang putuskan budget waktu render.

#### 2.8 Industri list dipotong dari ~25 jadi 5
Foto 10.51.19(1) ada 2 baris (kategori favorable + unfavorable), total **~25 industri**. Prompt minta dipotong jadi 5.

**Saran:** simpan list lengkap dari foto + boleh tambahan ringkasan top-5.
```
- career_industri_full:
  - kategori: favorable
    list: [鋼鐵工廠, 五金行, 採礦, 汽車, 機械, 科學家, 律師, 歌影星, 音樂家, 武術館, 會計, 金融界]
  - kategori: unfavorable / supportif lain
    list: [流血攤頭, 運動家, 介紹中人, 醫師, 清潔隊, 記者, 護士, 導遊, 馬戲團, 航海漁業, ...]
```

#### 2.9 Marriage tafsir konsekuensi
Foto 10.51.19(2) ada teks panjang konsekuensi:
- 忌: "夫妻不能合和終世, 破壞別離, 家世運未通, 命裏複雜, 敗家之兆, 終生不幸..."
- 宜: "締結良緣, 富貴成功, 勤儉建業, 老景倍加昌盛..."

**Prompt cuma ekstrak `marriage_cocok` & `marriage_hindari`** (cabang Hanzi). Konsekuensi text hilang.

**Saran field:**
```
- marriage_cocok_tafsir_raw: {konsekuensi/keuntungan dari foto}
- marriage_hindari_tafsir_raw: {konsekuensi negatif dari foto}
```

### KECIL — opsional tapi worth menambah

- **屬 shio Hanzi** (mis. 屬龍) — di kanan main grid
- **星期** (hari minggu lahir) — mis. 星期三
- **Software metadata**: 第72685號, 作者: 陳恩國, 程式設計, 電話 — bawah main grid (audit trail versi software)

---

## Ringkasan: Saran Action untuk Agent 1

### Phase 1 — Verifikasi (jangan terima mentah)
1. Cek tiap finding di kode existing:
   - Apakah `parse_md.py` sudah punya parser untuk field yang aku claim "tidak ada"? (Mungkin ada, prompt-nya saja yang belum minta.)
   - Apakah `templates/*.html` punya anchor untuk konten baru ini?
   - Apakah subjek MD existing (chelsey, keiko, wuhuanyang, liyuanqing) sudah ada partial extraction-nya tapi inkonsisten?
2. Validasi dengan render PDF subjek existing — lihat halaman mana yang sudah cukup vs yang butuh field baru.

### Phase 2 — Putuskan scope
1. Field mana **wajib** masuk schema baru (dampak besar ke kualitas output).
2. Field mana **opsional/tunda** (nice-to-have, tidak kritis).
3. Apakah perlu halaman PDF baru (mis. halaman 古書云, halaman 流年 lengkap) atau cukup tambah card di halaman existing.

### Phase 3 — Update artifact
1. Update `WEB_CLAUDE_PROMPT.md` (atau split jadi `MD_SCHEMA.md` + `EXTRACTION_GUIDE.md`).
2. Update `engines/parse_md.py` untuk handle field baru.
3. Update templates HTML + `engines/render.py` untuk tampilkan field baru.
4. Update `AUDIT_NOTES.md` dengan rincian perubahan.

### Phase 4 — Migration plan
1. Subjek existing (chelsey, keiko, wuhuanyang, liyuanqing) — re-extract dengan schema baru? Atau backward-compat (engine handle null untuk field baru, tampilkan "—")?
2. Test rendering full pipeline pakai subjek 李佳玲 (foto sudah lengkap di `foto\database\07-05-2026\1\`).

---

## Pertanyaan terbuka untuk Agent 1 putuskan

1. Apakah `WEB_CLAUDE_PROMPT.md` di-deprecate (Claude Web flow stop) atau dual-support?
2. Field 流年 grid 10-tahun — apakah render sebagai tabel di halaman da yun existing, atau butuh halaman baru?
3. 古書云 raw — render dengan font khusus / blockquote, atau diterjemahkan saja ke Indo?
4. Multi-star Zi Wei — apakah template halaman 16/17/18/19 perlu rebuild untuk akomodasi, atau cukup card detail per palace?

---

## TEMUAN 3 — Extraction Quality Report (request user, baru)

**Konteks:** User tidak bisa reshoot foto. Banyak foto Xing Qiao dari WhatsApp ada masalah
kualitas (miring, reflective glare, resolusi rendah, font kecil padat). Aku saat ekstrak
menemukan beberapa foto yang ambigu, tapi user perlu tahu **foto mana yang tidak jelas
dan kenapa** supaya bisa interpretasi PDF dengan konteks (tidak salah anggap data salah,
padahal foto-nya yang tidak terbaca).

### Yang user mau

Setelah `build_pdf.py` selesai, agent (Claude Code) keluarkan **Extraction Quality Report**
yang menjelaskan transparan:
- Foto mana yang tidak jelas
- Kenapa tidak jelas (miring / blurry / font kecil / multi-stars padat / dll)
- Field apa yang terdampak (null / low-confidence / paraphrase)
- Apa yang bikin agent bingung (mis. "stem mirip 戊 atau 戌")

### Format report yang aku rancang

Dikeluarkan ke chat di akhir pipeline + (opsional) disimpan ke
`v45/data/subjects/{subject_id}.quality_report.md`.

```
═══════════════════════════════════════════════════
📋 EXTRACTION QUALITY REPORT — {Subject Name}
═══════════════════════════════════════════════════

PDF: #result/{date}/{Name}-{Hanzi}-{Birth}.pdf
Total foto: N | Field terekstrak: M | Null: X | Low-confidence: Y

─── 🔴 FOTO TIDAK JELAS / DATA TIDAK PRESISI ───

[1] {filename}
    Layar: {layar apa, mis. Main BaZi grid}
    Masalah: {kenapa tidak jelas}
    Field terdampak:
    • {field_name} → null/low-confidence ({nilai})
    Kebingungan saya: {what made me uncertain}

─── 🟡 FOTO MEDIUM (raw paragraph kemungkinan tidak word-perfect) ───

[N] {filename}
    Masalah: ...
    Dampak: ...

─── 🟢 FOTO BAIK ───

X foto lainnya jelas, ekstraksi confidence tinggi.

─── 📊 RINGKASAN PER SECTION ───

✓ DATA dasar       : 100%
⚠ DATA detail     :  78%  ← foto [1][2]
✓ Tafsir section  : 100% prosa
⚠ Tafsir raw HZ   :  85%  ← foto [4]
...

Field null akan tampil "—" di PDF. Field low-confidence sudah di-render
tapi mungkin tidak 100% akurat. Bandingkan PDF vs foto untuk verifikasi.
═══════════════════════════════════════════════════
```

### Implementation hook

Aku track confidence inline saat ekstrak setiap field, dengan flag internal:
- `high` — foto jelas, value pasti
- `medium` — kebaca tapi keraguan minor
- `low` — kebaca tapi kemungkinan salah, sebut alternatif
- `null` — tidak terbaca

Akhir pipeline, format laporan dari flag-flag tersebut.

### Engine impact (untuk Agent 1 evaluasi)

**Minimal**: tidak ada perubahan engine wajib — laporan murni dihasilkan oleh Claude Code
saat ekstrak, di-output ke chat + ditulis ke `quality_report.md` (file baru di `data/subjects/`).

**Optional enhancement** (kalau Agent 1 mau lebih elegant):
1. Tambah field `## QUALITY` di MD schema, parser baca, lalu render-kan **subset critical**
   ke halaman akhir PDF (mis. di disclaimer page) sebagai notice "Beberapa data berasal
   dari foto yang tidak optimal — lihat: ...".
2. Atau: link QR / footer kecil di disclaimer page yang nunjuk ke `quality_report.md`
   kalau user kirim PDF + report sebagai paket.
3. Atau: cukup di-output ke chat saja, tidak perlu masuk PDF (paling ringan).

### Yang user mau Agent 1 tambah ke AUDIT_NOTES

Tambah entry:

> **Page X — Extraction Quality Report (NEW feature)**
> - Add quality_report.md output di `data/subjects/{id}.quality_report.md`
> - Output juga ke chat di akhir `build_pdf.py` (atau wrapper script `extract_and_build.py`)
> - Format: lihat handover Agent 2 section "TEMUAN 3"
> - Per field track confidence (high/medium/low/null) saat ekstrak
> - Engine impact: minimal (purely extraction-side), atau opsional tambah field MD
>   `## QUALITY` + render notice di disclaimer page

User butuh feature ini karena tidak bisa reshoot — transparency report = pengganti
quality control via reshoot. Tanpa ini, user akan keliru anggap data salah padahal
foto yang tidak terbaca.

---

---

## TEMUAN 4 — Konsistensi prinsip "no interpretation" untuk prosa/personalisasi (KRITIS)

**Konteks:** User berkali-kali tegaskan prinsip:
> "aku mau semua sumber dari foto, tidak ada interpretasi mu sendiri.
>  (nah tapi kalau penjelasan / prosa, itu intinya sesuai dari sumber foto,
>  kamu percantik tulisannya boleh)"

Prinsip ini **belum 100% konsisten** diikuti oleh prompt sekarang. Ada section di template
MD yang software Xing Qiao **tidak punya** tafsir asli, tapi prompt tetap minta diisi.

### Section yang foto Xing Qiao TIDAK ADA tafsir asli-nya

Berdasarkan inventaris foto subjek 李佳玲 (28 foto, layar 詳細解說 lengkap):

| Section MD | Foto Xing Qiao? | Strict-mode action |
|---|---|---|
| `radar_traits` (6-axis skor 0-10) | ❌ Tidak ada | null |
| `motto` (arketipe simbolik) | ❌ Tidak ada | null |
| `power / shadow / optimum` (4-bullet) | ❌ Tidak ada | null |
| `synthesis_trio` (kekuatan/tantangan/tindakan) | ❌ Tidak ada | null |
| `actions` (5 saran aksi praktis) | ❌ Tidak ada | null |
| `life_map` (lalu/sekarang/berikutnya) | ❌ Tidak ada | null |
| `quote` opening/closing | ❌ Tidak ada | null |
| `caifu_rules` (4 aturan emas rezeki) | ❌ Tidak ada | null |
| `yangzhai_zones` (6 zone arah hoki, beyond foto 陽宅 generic) | ⚠️ Sebagian | partial null |
| `career_industri` (5 industri searah dengan alasan personal) | ⚠️ Sebagian (foto ada list nama industri tanpa "alasan personal") | nama OK, alasan null |
| `dominant_star` label_id (label Indo "Bintang Perpindahan") | ⚠️ Hanzi ada, label Indo tidak | hanzi OK, label Indo null |

### Section yang foto ADA tafsir asli (boleh diterjemahkan + dipercantik)

Ini OK aku kerjakan karena prinsip "percantik tulisan dari sumber foto":

| Section MD | Foto Xing Qiao |
|---|---|
| Kepribadian paragraf | ✓ 性情 layar |
| 4 family card (pasangan/anak/saudara/kepemimpinan) | ⚠️ ada 婚配 + 夫妻 + 父母 + 兄弟宮 ZW palace, tapi tidak ada "saudara/kepemimpinan" eksplisit |
| Shen Sha paragraf | ✓ 神煞 layar |
| Caifu paragraf | ✓ 財帛 + 財富 layar |
| Career intro | ✓ 事業 layar |
| Day Master & Wu Xing caption | ⚠️ ada di main grid (體相 + wuxing) tapi prosa harus aku susun dari data |
| Yang Zhai paragraf | ✓ 陽宅 layar |
| Da Yun spotlight + 5 seasons | ⚠️ data da yun ada, tapi "spotlight phase sekarang" + season naming = aku susun dari data |
| Palace insight + action (12 palace) | ⚠️ ada 紫微論命 layar dengan multi-star per palace, prosa harus aku susun dari star list |
| Kesimpulan quote + stats | ⚠️ ada 全局總論 dengan tafsir umum |

### Pertanyaan KRITIS yang Agent 1 wajib putuskan

User pilih opsi mana untuk section "interpretive" (tabel pertama):

#### **Opsi A — Strict (100% prinsip user)**
- Section yang foto tidak punya tafsir → MD field = `null`
- Engine render: placeholder netral, atau template per-stem default (mis. 丁火 → "Lilin/Cahaya Hangat" generic)
- **PDF lebih kosong tapi 100% sumber foto.** Tidak ada konten "ngarang".
- Risk: PDF terasa kurang lengkap / kurang personal di section creative.

#### **Opsi B — Soft (default prompt sekarang)**
- Section yang foto tidak punya tafsir → Claude Code tulis interpretasi BaZi standar berdasarkan DATA
- Mis. radar_traits "確實 4, 創意 8, 守禮 7..." → derived dari DM 丁火 + format + 大運
- **PDF kaya tapi ada elemen interpretasi standar** (bukan ngarang, rule-based).
- Risk: melanggar prinsip user "no interpretation".

#### **Opsi C — Hybrid (rekomendasi Agent 2)**
- Section "berbasis tafsir asli" (kepribadian, palace insight, dayun, career, caifu, yang_zhai, kesimpulan) → **STRICT**: dari foto saja, kalau tidak ada → null.
- Section "creative wrapper" (radar, motto, power/shadow/optimum, trio synthesis, actions, quote, life_map, caifu_rules) → **boleh interpretasi BaZi standar** TAPI:
  - Wajib di-tag di Quality Report:
    ```
    ⓘ INTERPRETIVE CONTENT (derived, bukan langsung dari foto):
       - radar_traits: derived dari DM + format
       - motto: per-stem template
       - power/shadow/optimum: BaZi standard untuk DM 丁火
       - synthesis_trio: derived dari format + yong/ji + dayun current
       - actions: derived dari yong shen + dayun phase
       - caifu_rules: BaZi standard wealth management rule
    ```
  - Render PDF tetap full
  - User dapat: PDF kaya, transparan mana yang sumber foto vs derived.

### Implikasi ke artifact

- **Opsi A** → prompt revisi banyak section jadi "default null", template HTML perlu fallback elegant
- **Opsi B** → status quo, tapi user kemungkinan tidak puas
- **Opsi C** → prompt revisi field-by-field tag (`source: foto` / `source: derived`), Quality Report dibagi jadi 2 section (foto-quality + interpretive-disclosure), template HTML tidak perlu berubah

### Permintaan ke Agent 1

1. **Verifikasi tabel di atas** (section per section) — bandingkan dengan template HTML existing dan apa yang sudah dirender di subjek MD lama (chelsey/keiko/wuhuanyang). Cek apakah ada section yang sebenarnya **ada** di foto tapi aku miss waktu inventaris.
2. **Konfirmasi ke user**: opsi A / B / C — keputusan ini fundamental, mempengaruhi seluruh schema dan ekspektasi PDF.
3. Update prompt + parse_md.py + templates sesuai opsi terpilih.
4. Kalau pilih Opsi C: koordinasi dengan TEMUAN 3 (Quality Report) — gabungkan jadi 1 report dengan 2 section: "Foto Quality" + "Interpretive Disclosure".

User bilang "aku mau suruh agent 1 cek, ini penting soalnya." → user expect Agent 1 baca finding ini, validasi, lalu tanya user untuk pilih opsi A/B/C sebelum implementasi.

---

*— Agent 2 (Claude Code paralel), 2026-05-07*
*Update 2026-05-07 (1): tambah TEMUAN 3 (Extraction Quality Report) per request user.*
*Update 2026-05-07 (2): tambah TEMUAN 4 (konsistensi "no interpretation") per request user — KRITIS.*
