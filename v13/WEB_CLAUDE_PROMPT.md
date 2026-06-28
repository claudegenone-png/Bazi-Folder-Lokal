# PROMPT untuk Claude Web — Ekstrak Ramalan BaZi & Zi Wei untuk PDF V7 (Full-MD Mode)

> ## ⚠️ KOREKSI WAJIB (2026-05-21) — BACA DULU, OVERRIDE CONTOH DI BAWAH
> Beberapa field RENDER (yang muncul di PDF) di dokumen ini DULU dicontohkan di section
> `## DATA_EXTRA` / format nested. ITU SALAH → halaman PDF jadi KOSONG (build tetap sukses,
> jadi tidak ketahuan sampai PDF dilihat). Field berikut **WAJIB di section `## DATA`** dengan
> key & format PERSIS ini (rujukan kualitas: subjek `mrzul` & `bpa_test`):
>
> - `kesimpulan_narrative:` — 1 paragraf sintesis MENYELURUH (identitas, DM + skor, yong/ji shen,
>   istana hidup, industri, da yun, jodoh, kesehatan, hunian, puisi klasik), antar-bagian dipisah
>   ` || `. WAJIB ADA, kalau tidak halaman Kesimpulan kosong (cuma tampil "—").
> - `liu_nian_YYYY:` dengan nilai `umur|ganzhi|prosa` — 1 baris per tahun (mis. `liu_nian_2026: 26|丙午|...`).
> - Kalimat pertama prosa wajib dimulai `Tahun YYYY...`, tetapi struktur pembuka setiap tahun harus bervariasi. Jika foto memakai susunan berulang, parafrasekan secara profesional tanpa mengubah atau meringkas maknanya.
> - `gushu_quote_N:` dengan nilai `sumber_hz|sumber_id|teks_hz|teks_id` — 1 baris per kutipan klasik 古書云.
> - `xiongnian_list:` `32, 36, 47, ...` (usia rawan, dipisah koma).
> - `ziwei_su_ming:` prosa 宿命.
> - `shiye_favorable_full:` & `shiye_supportive_full:` — `hz|Indo, hz|Indo, ...` (daftar 事業 PENUH,
>   tidak dipotong; TERPISAH dari blok `industri:` 5-tag di section TAFSIR).
>   **⚠️ ATURAN FOLDER (2026-06-05):** Foto 事業 bisa ada di `data/` (bukan `transelate/`).
>   Translator agent hanya baca `transelate/` — kalau foto 事業 ada di `data/`, **MAIN agent WAJIB**
>   ekstrak langsung dua field ini ke `## DATA`. JANGAN skip hanya karena foto di `data/`.
>   Format: `shiye_favorable_full: hz|Indo, hz|Indo, ...` dan `shiye_supportive_full: hz|Indo, hz|Indo, ...`
>   (baris 1 = favorable ◎, baris 2 = supportive ◎ — urutan sesuai di foto).
> - `marriage_cocok_tafsir:` & `marriage_hindari_tafsir:` — prosa tier 大吉 / 次吉 / 忌.
> - `format:` — label format 格局 WAJIB ditulis ke `## DATA` (mis. `正官格`, `偏財格`, `食神格`).
>   Kalau tidak ada → halaman FORMAT card tampil semua "—". JANGAN tulis null kalau foto ada labelnya.
> - `yang_zhai_gua:` — 1 hanzi gua (mis. `兌`, `坎`, `離`) WAJIB ditulis ke `## DATA` sebagai
>   **trigger field halaman Yang Zhai**. Kalau field ini tidak ada, halaman Yang Zhai di-SKIP
>   meski semua `yang_zhai_zone_*` sudah ditulis. Null hanya kalau foto tidak ada label gua.
>
> **Skala skor DM (PENTING):** ambil dari grid `日主旺度`, lalu **KALIKAN 1000**
> (grid `+3.900 / -4.748` → `dm_pos_score: 3900`, `dm_neg_score: 4748`).
> JANGAN tulis 3.9 / 4.748 (bar Kekuatan DM jadi rusak/absurd).
>
> **Aturan inti:** `## DATA` = DIRENDER ke PDF. `## DATA_EXTRA` = ARSIP, di-SKIP parse_md (TIDAK
> muncul di PDF). Kalau ragu sebuah field perlu tampil di PDF, taruh di `## DATA`.
> Engine V7.1 = FREEZE: semua perbaikan di MD/doc, JANGAN ubah kode engine atau template.


> **V7.1 DAILY RENDER POLISH (2026-05-15)** — guidelines untuk MD writing supaya PDF rapi:
>
> **Marriage (page 7)** — kalau foto sebut "其他生相次吉" (other shios are 次吉 generally compatible):
> - `marriage_cocok`: tulis HANYA shio 大吉 (biasanya 3 shios) — JANGAN expand jadi 8+ entries.
> - Sebutan 次吉 implicit di tafsir text aja, bukan field list. Display lebih bersih.
>
> **Yang Zhai zones (page 9)** — boleh tulis 北方 atau 北 (engine auto-strip 方/向 suffix sejak 2026-05-15).
>
> **Kesehatan (page 12)** — WAJIB isi 3 field DATA section:
> - `jie_e_palace_hz`: foto 疾厄 verbatim hanzi prose
> - `jie_e_palace_id`: terjemahan Indonesia line-by-line dengan [[hz]] tags
> - `jie_e_organ_focus_id`: 1 kalimat ringkas "Yang utama wajib dijaga: ..."
>
> **12 ISTANA WAJIB LENGKAP (2026-05-21):** SEMUA 12 narasi istana 詳細解說 (命宮/兄弟/夫妻/子女/財帛/疾厄/遷移/僕役/官祿/田宅/福德/父母) diterjemahkan **PENUH & faithful** dari foto ke `palace_*_insight` — JANGAN diringkas (termasuk klausa kondisional "如與X同宮"). Bukan hanya 命宮. Layar narasi buram WAJIB di-enhance (contrast+sharpen+upscale) lalu baca ulang sebelum tulis MD. preflight.py memberi warning otomatis kalau insight istana < 220 char (dicurigai diringkas). Karier(官祿)+Rezeki(財帛) sering panjang — pastikan penuh.
>
> **12 Palace prose (TAFSIR section palace1/2/3)** — format `insight` field:
> - JANGAN tulis "Foto X verbatim: '...hanzi...' || **Terjemahan**: ..." prefix
> - LANGSUNG tulis Indonesian translation, dengan inline [[hz]] tags untuk phrase kunci
> - Palace template font sudah 12pt (was 10pt) untuk readability lebih
>
> **Karir & Industri (TAFSIR)** — wajib format struktural:
> ```
> ### Karir & Industri
> tags:
>   - fav_1: hz: <unsur>; label: <Indonesia>
>   - fav_2: hz: <unsur>; label: <Indonesia>
>   - unfav_1: hz: <unsur>; label: <Indonesia>
>   - unfav_2: hz: <unsur>; label: <Indonesia>
> industri:
>   - nama: <Industri>; unsur: <hz>; alasan: <foto sumber>
>   (5 entries)
> ```
> Format `- nama: X; unsur: Y; alasan: Z` (semicolon-separated). Header "### Karir & Industri" persis.
>
> **Sintesis & Saran Aksi (TAFSIR)** — wajib 5 actions:
> ```
> ### Sintesis & Saran Aksi
> opening: <1 kalimat opening>
> actions:
> - title: <action 1>; context: <foto sumber + alasan>
> - title: <action 2>; context: ...
> (5 entries)
> ```
> Tanpa 5 actions, page 30 cuma tampil 1 default placeholder.


> **V7 vs V4.5/V4.9:**
> V7 = V4.5 + foto-first enrichment per halaman. Setiap phase punya tabel cost-benefit
> untuk decide field mana yang masuk PDF.
>
> Strict: SEMUA field dari foto (NO compute layer). Foto tidak ada → null = block hidden.
>
> **Phase 1 Page 04 status:** DROPPED 2026-05-08 (low ROI, foto coverage tidak
> guaranteed). Engine code latent (capability tetap ada, MD bisa pakai kalau perlu).



> **Cara pakai:** Buka [claude.ai](https://claude.ai), upload semua foto Xing Qiao subjek (termasuk layar `批命備註` untuk skor 旺度 dan layar `神煞`), lalu copy-paste seluruh prompt di bawah ini ke chat. Output Claude Web = 1 file markdown. Simpan ke `v45/data/subjects/{nama}.md`.
>
> **Mode:** Full-MD (V4.5) — engine TIDAK compute apa-apa, semua data dari foto. Kalau foto tidak punya datanya → field `null`, di PDF akan tampil "—" / blank. **TIDAK ADA fallback** (tidak ada default `正官格`, tidak ada simple DM threshold, tidak ada auto-derive marriage, tidak ada native-compute pilar).
>
> **Foto yang WAJIB ada** untuk full-MD mode:
> 1. Grid BaZi utama (4 pilar + da yun row + nama + tanggal lahir + format)
> 2. **批命備註** — skor 旺度 per stem + DM pos/neg score (paling kritis, ini sumber DM strength)
> 3. **神煞** / 星煞 — list shen sha aktif + lokasi pilar
> 4. Layar Zi Wei (12 palace + ming gong + shen gong + bintang lengkap, bukan cuma main star)
> 5. Layar 陽宅 — gua trigram + arah hoki
> 6. **婚配** — list cocok / hindari shio (untuk marriage_cocok / marriage_hindari)
> 7. **先天體檢** — count per stem + mapping organ (甲膽 乙肝 dll)
>
> **Foto OPSIONAL untuk DATA_EXTRA** (data arsip, belum dipakai PDF tapi WAJIB ekstrak kalau fotonya ada):
> - 古書云 — kutipan klasik tentang day master
> - 全局總論 — ringkasan global
> - 父母 BaZi (bukan Zi Wei) — analisis ortu via 4 pilar
> - 事業 — bidang karir spesifik
> - 性情 — kepribadian detail
> - 流年易鑑 / 流年判斷 — tabel multi-usia + prediksi 5 tahun ke depan

---

## PROMPT (paste mulai dari baris di bawah ke Claude Web)

Anda adalah asisten ekstraksi BaZi & Zi Wei dari foto software Xing Qiao NCC. Saya akan upload beberapa foto screenshot software ramalan. Tugas Anda: hasilkan **satu file markdown** dengan struktur PERSIS seperti template di bawah, untuk dipakai engine PDF V4.5 di komputer saya.

aku akan kirim foto2nya dalam 2 batch, jangan buat dulu sampai aku suruh, output "oke" saja

### ATURAN UMUM (WAJIB DIIKUTI)

1. **Output: HANYA markdown final** — tanpa kata pengantar, tanpa penjelasan, tanpa code-fence di luar. Mulai langsung dari `# {Nama}` di baris pertama.
2. **Bahasa: Indonesia** (tafsir-nya). Hanzi/pinyin diselipkan untuk istilah teknis.
3. **Konvensi Hanzi**: setiap kali Anda menyebut karakter Hanzi (1-4 karakter, mis. pilar/ten god/format/star), bungkus dengan `[[...]]`. Contoh: `[[辛金]]`, `[[正官格]]`, `[[紫微]]`. Engine akan ubah ke styling khusus. Jangan bungkus seluruh kalimat — hanya istilah teknis Hanzi-nya.
4. **Budget kata** (WAJIB ditaati, ada catatan di tiap section). Kalau lebih → engine warning, layout PDF bisa pecah.
5. **Konsistensi DATA → TAFSIR**: prosa di TAFSIR harus mengacu ke nilai di section `## DATA`. Jangan menyebut "Logam" kalau day master-nya Air. Jangan menyebut "fase 27-37" kalau da yun current 29-38.
6. **DILARANG pakai em-dash (—) atau en-dash (–) sebagai pemisah klausa.** Ganti dengan **koma (,)** atau **titik (.)**. Ini berlaku untuk SEMUA tafsir & deskripsi. Contoh:
   - ❌ "Keiko adalah api yang hangat — namun perlu disalurkan"
   - ✅ "Keiko adalah api yang hangat, namun perlu disalurkan"

### RULE 7 — PALACE & LIU_NIAN BINDING (Anti-Halusinasi, 2026-05-24)

**Akar masalah BPA test (2026-05-23):** halusinasi `palace_zinu_insight` ambil konten dari 全局總論 (foto general), bukan dari foto 子女 specific. Halusinasi `palace_puyi_insight` drop paragraf 2-3 dari foto 僕役 yang punya 3 paragraf. Halusinasi `liu_nian_2026` pakai konten foto tahun lain. Cegah dengan binding strict ini:

#### 7.1 — Source binding deterministik (1-to-1 mapping)

SETIAP field palace insight HANYA boleh sumbernya dari foto palace yang persis cocok:

| Field MD | Source foto WAJIB | DILARANG ambil dari |
|---|---|---|
| `palace_ming_gong_insight` | Foto layar **【命宮】** | 全局總論, palace lain |
| `palace_xiongdi_insight` | Foto **【兄弟】** | 全局總論, palace lain |
| `palace_fuqi_insight` | Foto **【夫妻】** | 全局總論, marriage foto |
| `palace_zinu_insight` | Foto **【子女】** | 全局總論, fumu foto |
| `palace_caibo_insight` | Foto **【財帛】** | 全局總論, palace lain |
| `palace_jie_e_insight` | Foto **【疾厄】** | 全局總論, palace lain |
| `palace_qianyi_insight` | Foto **【遷移】** | 全局總論, palace lain |
| `palace_puyi_insight` | Foto **【僕役】** | 全局總論, palace lain |
| `palace_guanlu_insight` | Foto **【官祿】** | 全局總論, 事業 foto |
| `palace_tianzhai_insight` | Foto **【田宅】** | 全局總論, palace lain |
| `palace_fude_insight` | Foto **【福德】** | 全局總論, palace lain |
| `palace_fumu_insight` | Foto **【父母】** | 全局總論, zinu foto |

Liu Nian binding:
| Field | Source foto WAJIB |
|---|---|
| `liu_nian_YYYY` | Foto **流年判斷** yang KHUSUS tahun YYYY |

**Cross-foto enrichment** (mis. dari 全局總論) BOLEH, tapi WAJIB:
- Tag eksplisit di prosa: "Menurut 全局總論, ..."
- Tidak menggantikan konten foto palace specific
- Maksimal 1-2 kalimat enrichment per insight

**Kalau foto palace specific TIDAK ADA** (mis. foto 兄弟 tidak ter-upload):
- Set `palace_xiongdi_insight: null`
- Tulis di `## CATATAN`: "palace_xiongdi tidak ada foto specific"
- **JANGAN diisi dari foto general** (halusinasi)

#### 7.2 — Verbatim klausa count (Anti-Drop Paragraf)

Foto narasi sering punya 2-5 paragraf. Engine sering compress jadi 1 paragraf saja → konten hilang.

**ATURAN STRICT:**
1. Translate **SEMUA paragraf** dari foto — jangan drop P2/P3/P4/P5.
2. Klausa kondisional (`如與X同宮`, `位於Y之宮內`) WAJIB diterjemahkan, jangan skip.
3. Tiap konsep di foto harus ada di insight — tidak boleh ada konten yang hilang.

#### 7.3 — Verbatim translation (Anti-Mistranslate)

Frasa Hanzi nuanced WAJIB literal:
- `絕無惡意` = "sama sekali tanpa niat buruk", BUKAN "tidak pernah lepas dari kekhawatiran"
- `厭惡謊事` = "benci kebohongan", BUKAN "tidak suka hal menyebalkan"
- `雙親平常穩重，一旦發怒火山爆發` = "**orang tua** biasanya tenang, sekali marah seperti gunung meletus" (subjek = orang tua, BUKAN BPA kesabaran meledak)

**Self-check tiap kalimat:** identifikasi subjek + verb + objek di Hanzi, pastikan terjemahan match.

#### 7.4 — Foto buram WAJIB enhance dulu

(Lihat juga AUTORUN.md aturan no. 2)
- Sebelum tulis insight dari foto narasi, kalau Read awal Hanzi tampak buram/ambigu → STOP.
- Jalankan: `python v7.1/narrative_crop.py <foto> <_AUDIT_LOGS/enh/{stem}_enh.jpg>` (PIL Contrast 1.5 + Sharpness 2.2 + 2x LANCZOS).
- Read enhanced version, baru tulis insight.
- Foto yang gagal terbaca walau sudah enhanced → set field null + lapor di CATATAN, **JANGAN halusinasi**.

#### 7.5 — Self-validate checklist (sebelum exit)

Sebelum return MD ke user, untuk SETIAP palace insight:
- [ ] Source foto persis cocok (RULE 7.1)
- [ ] Klausa count ≥80% foto sumber (RULE 7.2)
- [ ] Hanzi nuanced di-translate literal (RULE 7.3)
- [ ] Foto buram sudah di-enhance (RULE 7.4)
- [ ] Insight tidak include konten dari foto lain (kecuali tagged "Menurut 全局總論, ...")

Untuk SETIAP liu_nian_YYYY:
- [ ] Source foto khusus tahun YYYY (bukan tahun lain)
- [ ] Shen sha + tier sesuai foto (bukan default/halusinasi)

### ATURAN UNTUK SECTION `## DATA`

#### Field wajib terbaca (5 field minimum)
nama, hanzi, gender, tanggal lahir, jam lahir. Kalau benar-benar tidak ada di foto, tulis `null` + tulis di `## CATATAN`.

#### Tanggal lahir — HANYA SOLAR (公曆/陽曆/國曆/西元)

**Software Xing Qiao biasanya tampil 2 baris tanggal di info-box pusat:**
- Baris 1: `國曆民國 XX年 M月 D日` (atau `西元 YYYY年 M月 D日` / `公曆 ...`) → **INI YANG DIPAKAI (SOLAR)**
- Baris 2: `農曆 [年柱hz] XX年 M月 D日` (atau `陰曆 ...`) → **JANGAN DIPAKAI (LUNAR)**

**Step-by-step ekstraksi tanggal:**
1. Cari di foto baris yang berlabel **`國曆`** atau **`西元`** atau **`公曆`** atau **`陽曆`** (biasanya baris pertama / paling atas)
2. Ambil angka `年/月/日` dari baris itu SAJA
3. Konversi ROC ke Gregorian kalau perlu: **西元 = ROC民國年 + 1911** (mis. 民國97年 → 1911 + 97 = 2008)
4. Format ke `YYYY-MM-DD`

**Contoh konkret (DARI KASUS NYATA YANG PERNAH SALAH):**
Foto menunjukkan:
```
國曆民國 97年 2月 18日 8時生
農曆戊子 97年 1月 12日 8時生
```
- ✅ BENAR: `lahir_tanggal: 2008-02-18` (dari baris 國曆, ROC 97 → 2008)
- ❌ SALAH: `lahir_tanggal: 2008-01-12` (jangan ambil "1月12日" dari baris 農曆!)

Kalau baris 國曆/西元/公曆/陽曆 **tidak ada / tidak terbaca** → tulis `lahir_tanggal: null`, JANGAN konversi lunar→solar sendiri.

#### Pilar 4-柱 — baca dari MAIN BAZI grid

**Sumber resmi pilar = layar utama BaZi yang menampilkan grid 4 kolom (時 月 日 年 atau 年 月 日 時).** Biasanya foto utama / cover. JANGAN ambil pilar dari layar Zi Wei atau layar tafsir lainnya.

**Hati-hati urutan kolom**: software Chinese tradisional sering pakai urutan **kanan-ke-kiri**: 時 → 日 → 月 → 年 (kanan = kiri). Pastikan kamu identifikasi label kolom dengan benar.

**Disambiguasi Hanzi mirip — list kritis:**

Stems (天干, 10 karakter):
- 乙 ≠ 己 ≠ 已 (perhatikan garis bawah)
- 戊 ≠ 戌 (戊=stem, 戌=branch) ≠ 戍
- 壬 ≠ 王
- 庚 ≠ 唐 ≠ 庫
- 辛 ≠ 幸
- 丙 ≠ 内
- 癸 — sering salah baca jadi 癲 atau 登

Branches (地支, 12 karakter — wajib tahu nama shio-nya juga):
- 子 (Tikus) ≠ 戌 (Anjing) ≠ 戊 (stem) — visually distinct tapi sering tertukar
- 卯 (Kelinci) ≠ 印 (印=ten god label, BUKAN branch) ≠ 卵
- 寅 (Macan) ≠ 演 ≠ 寘
- 辰 (Naga) ≠ 唇 ≠ 振
- 酉 (Ayam) ≠ 西 (西=barat, bukan branch)
- 巳 (Ular) ≠ 已 (sudah) ≠ 己 (stem)

**Pilar HARI (日柱) PALING KRITIS** — stem-nya = Day Master, dipakai untuk seluruh tafsir. Triple-check pilar hari dari grid utama BaZi. Kalau ragu sedikit pun → tulis `null` (dalam mode full-MD, engine TIDAK auto-compute pilar — null akan tampil "—" di PDF).

#### Pilar — re-check by visual matching only

Kalau pilar foto kelihatan ambigu (misalnya stem mirip 戊/戌, 己/巳), bandingkan visual stroke-nya dengan referensi disambiguasi di atas. **JANGAN pakai aturan kalkulasi (五虎遁/五鼠遁) untuk validasi** — itu tugas software, bukan tugas pembaca foto. Kalau ragu setelah disambiguasi visual → tulis `null` untuk pilar yang ragu, **TIDAK ADA fallback compute** di mode full-MD.

#### Marriage cocok / hindari — WAJIB dari layar 婚配 di software

Software Xing Qiao biasanya punya layar khusus `婚配` (matchmaking) yang menampilkan tabel cocok / hindari **secara eksplisit dalam nama shio** (mis. "Hindari: 牛/兔/狗/龍" / "Cocok: 鼠/猴/雞").

**WAJIB:** baca dari layar 婚配 itu, **JANGAN derive sendiri dari day branch** (三合/六合/六沖/六害/三刑 BUKAN tugas pembaca foto, itu tugas software).

**Konversi shio Hanzi → branch Hanzi (untuk output):**

| Shio (foto) | Branch (output) | | Shio (foto) | Branch (output) |
|---|---|---|---|---|
| 鼠 Tikus | 子 | | 馬 Kuda | 午 |
| 牛 Kerbau | 丑 | | 羊 Kambing | 未 |
| 虎 Macan | 寅 | | 猴 Monyet | 申 |
| 兔 Kelinci | 卯 | | 雞 Ayam | 酉 |
| 龍 Naga | 辰 | | 狗 Anjing | 戌 |
| 蛇 Ular | 巳 | | 豬 Babi | 亥 |

**Aturan output:**
- ✅ `marriage_cocok: 子, 申, 酉` (cabang Hanzi, bukan nama shio)
- ❌ `marriage_cocok: 鼠, 猴, 雞` (jangan tulis shio Hanzi)
- ❌ `marriage_cocok: Tikus, Monyet, Ayam` (jangan tulis nama Indo)
- Jumlah cocok / hindari **ikuti foto persis** (bisa 2, 3, 4, atau 5 entries — JANGAN dipotong/ditambah).
- Kalau foto tidak punya layar 婚配 → `marriage_cocok: null` dan `marriage_hindari: null`. **JANGAN derive dari day branch.**

#### Field interpretatif (yong_shen, ji_shen, format) — WAJIB DARI FOTO

Mode full-MD (V4.5) **TIDAK MENGINTERPRETASI**. Field-field ini WAJIB terbaca eksplisit dari foto:

- `yong_shen` — biasanya muncul di layar 用神/喜神 atau di 批命備註 sebagai label (mis. "用神: 金水")
- `ji_shen` — sama, muncul sebagai label (mis. "忌神: 火土")
- `format` — label format (mis. `偏印格`, `正官格`) muncul di header layar BaZi atau layar 八字論斷 / 卦格 / 詳細解說

**Kalau salah satu tidak terbaca:** tulis `null` + catat di `## CATATAN` bahwa field ini tidak ditemukan di foto. **JANGAN ngarang berdasarkan distribusi 十神 atau dominasi unsur.** Mode full-MD = pure foto extraction.

#### Field lain
Kalau tidak terbaca foto → tulis `null`. JANGAN tebak. **Mode full-MD: TIDAK ADA engine native-compute** untuk pilar/da yun/wuxing/shio. Field null akan tampil "—" di PDF, atau memicu warning saat build.

---

### ⭐ FIELD TAMBAHAN — FULL-MD MODE (V4.5 tanpa engine compute)

Untuk mode **semua data dari foto** (engine TIDAK compute apa-apa), foto-foto Xing Qiao biasanya menampilkan layar tambahan ini. Cari layar-layar berikut dan ekstrak datanya:

#### Layar `批命備註` (Skor 旺度 / Day Master Strength) — WAJIB dicari

Layar ini berisi tabel skor numerik per-stem (10 baris) + total per-elemen + skor 主旺/主衰. Foto biasanya berjudul `批命備註` atau `星僑批命` atau menunjukkan list seperti `甲木(傷官)的旺度=1430`.

**Field yang harus diisi:**

```
- wangdu_jia_mu: {skor 甲木, mis. 1430}
- wangdu_yi_mu: {skor 乙木, mis. 330}
- wangdu_bing_huo: {skor 丙火, mis. 0}
- wangdu_ding_huo: {skor 丁火, mis. 1060}
- wangdu_wu_tu: {skor 戊土, mis. 1650}
- wangdu_ji_tu: {skor 己土, mis. 550}
- wangdu_geng_jin: {skor 庚金, mis. 0}
- wangdu_xin_jin: {skor 辛金, mis. 220}
- wangdu_ren_shui: {skor 壬水, mis. 728}
- wangdu_gui_shui: {skor 癸水, mis. 2600}

# Total per elemen (sum dari 2 stem masing-masing elemen)
- wangdu_total_mu: {木 total, mis. 1760}
- wangdu_total_huo: {火 total, mis. 1060}
- wangdu_total_tu: {土 total, mis. 2200}
- wangdu_total_jin: {金 total, mis. 220}
- wangdu_total_shui: {水 total, mis. 3328}

# Day Master Strength (paling kritis)
- dm_pos_score: {主旺 / supporting score, mis. 3548}
- dm_neg_score: {主衰 / opposing score, mis. 5020}
- dm_strength: {旺 / 弱 / 平}     # 旺=Kuat, 弱=Lemah, 平=Seimbang
- dm_strength_label_id: {Kuat / Lemah / Seimbang}
```

**Aturan derivasi `dm_strength`:**
- `dm_pos_score > dm_neg_score` → `旺` (Kuat)
- `dm_pos_score < dm_neg_score` → `弱` (Lemah)
- selisih ≤ 10% → `平` (Seimbang)

**KALAU foto 批命備註 tidak ada / tidak terbaca:** isi semua wangdu_* dan dm_* dengan `null`. JANGAN estimasi sendiri. `wuxing_jin/shui/mu/huo/tu` HARUS dari `xiantian_*` (per-stem count di 先天體檢) — kalau itu juga tidak ada, semua null. **JANGAN estimasi proporsional dari pilar — itu engine logic, bukan foto extraction.**

#### Da Yun — arah & start age (dari layar utama BaZi)

Di grid BaZi utama, biasanya ada baris bawah grid yang menampilkan 10 cycle 大運 dengan **umur start eksplisit** (mis. `9 19 29 39 49 59 69 79 89 99` di atas pilar 己卯 戊寅 丁丑 ...).

```
- da_yun_arah: {順行 / 逆行}     # forward/backward
- da_yun_start_age: {umur cycle pertama, mis. 9. WAJIB sama dengan angka pertama di field da_yun.}
```

**Cara baca arah:**
- Cycle stem-branch bergerak **mundur** di siklus 60 jiazi (mis. dari 庚午 → 己巳 → 戊辰) = `逆行`
- Cycle bergerak **maju** (mis. dari 庚午 → 辛未 → 壬申) = `順行`

**Konsistensi:** field `da_yun` sudah punya umur start (mis. `9:己卯, ...`). `da_yun_start_age` harus = angka pertama itu. `da_yun_arah` harus konsisten dengan urutan stem-branch di field `da_yun`.

#### Shen Sha — list lengkap dari foto (bukan compute)

Layar `星煞` / `神煞` di Xing Qiao biasanya menampilkan list bintang aktif + lokasi pilarnya (年/月/日/時). Software NCCTaiwan menampilkan ini di tabel di bawah pilar.

```
- shen_sha_list: <!-- Daftar bintang yang TERBACA di foto, dipisah koma. Format dual:
  - Kalau foto tampilkan kolom pilar eksplisit: "{nama_hz}@{pilar}" (mis. 天乙貴人@日, 文昌@月)
  - Kalau foto cuma list flat (no pillar info): "{nama_hz}" saja, NO @tag (mis. 驛馬, 劫煞, 孤辰, 天醫)
  JANGAN inject @日 default kalau foto tidak ada info pilar — itu fabrikasi. -->
  contoh foto-with-pillar: 天乙貴人@日, 文昌@月, 驛馬@時
  contoh foto-flat: 驛馬, 劫煞, 孤辰, 天醫
```

Pilar di-encode `年/月/日/時`. Kalau bintang aktif di multiple pilar, tulis dengan koma terpisah (mis. `天乙貴人@日, 天乙貴人@時`).

**KALAU layar shen sha tidak ada / tidak terbaca:** tulis `shen_sha_list: null`. Di PDF, kartu shen sha akan tampil blank — TIDAK ADA fallback engine compute.

#### Format (格局) — ekstraksi langsung

Field `format` harus terbaca **eksplisit dari foto**. Software Xing Qiao biasanya menampilkan label format di header layar BaZi atau di layar 八字論斷. Cari label seperti `正官格` / `偏財格` / `食神格` / `傷官格` / `七殺格` / `偏印格` / `正印格` / `比肩格` / `劫財格` / `建祿格` / `羊刃格`.

**JANGAN tebak format dari distribusi 十神 sendiri.** Kalau tidak terbaca → `format: null` + catat di `## CATATAN`. Di PDF kartu format akan tampil "—" — TIDAK ADA default `正官格`.

#### Na Yin (納音) per pilar — opsional

Foto kadang menampilkan na yin di samping setiap pilar (mis. `海中金 / 大林木 / 山頭火`).

```
- nayin_tahun: {nama na yin tahun, mis. 海中金}
- nayin_bulan: {nama na yin bulan, mis. 大林木}
- nayin_hari: {nama na yin hari, mis. 山頭火}
- nayin_jam: {nama na yin jam, mis. 桑柘木}
```

Kalau tidak terbaca → semua `null`. Field ini display-only, tidak kritis.

#### Hidden Stems (藏干) per pilar — opsional

Foto kadang menampilkan藏干 di bawah branch tiap pilar (1-3 stem hanzi).

```
- canggan_tahun: {1-3 hanzi, mis. 戊乙癸 untuk 辰}
- canggan_bulan: {1-3 hanzi}
- canggan_hari: {1-3 hanzi}
- canggan_jam: {1-3 hanzi}
```

Kalau tidak terbaca → `null`. Field ini referensi tafsir, tidak kritis untuk PDF.

### ATURAN UNTUK SECTION `## TAFSIR`

- **Kalau di foto ADA tafsir asli** untuk section X → tulis ulang dalam bahasa Indonesia, ringkas, ikut budget kata.
- **Kalau di foto TIDAK ADA tafsir** untuk section X → tulis interpretasi BaZi/Zi Wei standar berdasarkan DATA yang sudah terbaca. JANGAN dikosongkan. JANGAN tulis "(tidak terbaca)".
- **Tone**: ramah-awam Indonesia, hindari jargon yang tidak dijelaskan, tulis untuk orang awam yang **tidak baca Hanzi**.

#### ⚠️ ANTI-FABRICATION RULE (KRITIS untuk strict-MD)

Untuk section creative wrapper (radar_traits, motto, power/shadow/optimum, sintesis trio, actions, kesimpulan, life_map, 5 seasons, da yun spotlight, caifu rules) yang foto NCC memang **TIDAK punya source eksplisit**:

✅ **Boleh:** interpretasi BaZi-standard yang **derived dari DATA section** (pilar, format, yong/ji, da_yun current cycle, ten god distribution).
- Mis. radar score derived dari distribusi 十神 + DM strength
- Mis. sintesis kekuatan derived dari format + yong shen
- Mis. da_yun spotlight bullets derived dari ten_god current cycle

❌ **JANGAN:**
- Fabricate **bidang/profesi/aktivitas/nama tempat** yang tidak terkait DATA (mis. "Industri Pendidikan dan Pelatihan" cuma karena yong=木 — fabrikasi).
- Fabricate **alasan personal** untuk profesi yang tidak ada di foto (mis. industri.alasan ngarang "Kreativitas dan empati halus" padahal foto 事業 cuma list nama profesi tanpa tafsir).
- Tambah/kurangi **list shio/profesi** dari foto eksplisit (foto kasih 3 cocok → MD harus 3, bukan 4).
- Inject **default tag** (mis. shen_sha @日 padahal foto tidak ada info pilar).

**Filosofi:** strict-MD = "structured field foto-source 100%, creative wrapper grounded di DATA section."

---

## TEMPLATE OUTPUT (ikuti struktur PERSIS ini)

```markdown
# {NamaIndo} {[[NamaHanzi]]}

## DATA

- nama: {NamaIndo}
- hanzi: {NamaHanzi 2-4 karakter ATAU null jika nama subjek English-only / tidak ada Hanzi resmi di foto. JANGAN ngarang transliterasi fonetis.}
- gender: {Pria | Wanita}
- gender_hz: {陽男 | 陰男 | 陽女 | 陰女 — eksplisit dari foto label (biasanya di header layar Zi Wei chart). Null kalau foto tidak label. Engine derive dari Pria/Wanita kalau null.}
- lahir_tanggal: {YYYY-MM-DD}
- lahir_jam: {HH:MM} (24-jam)
- pilar_tahun: {stem}/{branch}    # contoh 辛/未
- pilar_bulan: {stem}/{branch}
- pilar_hari: {stem}/{branch}
- pilar_jam: {stem}/{branch}

# Shio (屬) — eksplisit dari foto label "屬X" di main BaZi grid
- shio_hz: {1 hanzi shio, mis. 龍 (Naga) atau 鼠 (Tikus) atau null kalau tidak terbaca}

# === 先天體檢 per-stem count (count visible per 10 stems) ===
# Layar 先天體檢 (atau di samping pilar) tampilkan angka per stem. Mis. "甲1, 乙1, 丙1, 丁2, 戊2, 己0, 庚2, 辛0, 壬2, 癸1".
# WAJIB tulis 10 field di bawah kalau foto 先天體檢 ada. Null = foto tidak ada.
- xiantian_jia: {0-9 atau null}
- xiantian_yi: {0-9 atau null}
- xiantian_bing: {0-9 atau null}
- xiantian_ding: {0-9 atau null}
- xiantian_wu: {0-9 atau null}
- xiantian_ji: {0-9 atau null}
- xiantian_geng: {0-9 atau null}
- xiantian_xin: {0-9 atau null}
- xiantian_ren: {0-9 atau null}
- xiantian_gui: {0-9 atau null}

# === wuxing total (jumlah 2 stem per elemen, 0-18) ===
# Aturan: wuxing_mu = xiantian_jia + xiantian_yi, dst.
# Kalau xiantian_* null (foto tidak ada), tulis null di sini juga. JANGAN estimasi sendiri.
- wuxing_jin: {jumlah xin+geng atau null}
- wuxing_shui: {jumlah ren+gui atau null}
- wuxing_mu: {jumlah jia+yi atau null}
- wuxing_huo: {jumlah bing+ding atau null}
- wuxing_tu: {jumlah wu+ji atau null}
- yong_shen: {1 elemen Hanzi 用神 dari foto, mis. 水 — null kalau foto tidak ada}
- ji_shen: {1 elemen Hanzi 忌神 dari foto, mis. 火 — null kalau foto tidak ada}
- xi_yong_shen: {1 elemen Hanzi 喜用神 dari foto main grid (kolom kiri 5-shen), mis. 木 — null kalau foto cuma kasih 2-shen}
- xian_shen: {1 elemen Hanzi 閒神 dari foto, mis. 土 — null kalau foto tidak ada}
- chou_shen: {1 elemen Hanzi 仇神 dari foto, mis. 金 — null kalau foto tidak ada}
- shi_shen_per_pilar_tahun: {十神 label di atas year stem dari foto main grid, mis. 偏官 — null kalau foto tidak terbaca}
- shi_shen_per_pilar_bulan: {十神 label month stem, mis. 比肩 — null kalau tidak terbaca}
- shi_shen_per_pilar_hari: {biasanya 主 (subject sendiri), atau day stem ten god — null kalau tidak terbaca}
- shi_shen_per_pilar_jam: {十神 label hour stem, mis. 傷官 — null kalau tidak terbaca}
- ming_gong_bazi: {命宮 stem-branch dari foto main BaZi grid (BUKAN ziwei_ming_gong yang cabang only), mis. 乙卯 — null kalau tidak terbaca}

# === 體相 (5-Element Seasonal Status) — render ke badge lingkaran di Page 6 dme-card ===
# Sumber: foto Main BaZi grid kolom 體相 (sebelah kolom 旺度).
# Format foto: "木旺 火相 土死 金休 水囚" — split jadi 5 fields per element.
# Status valid: 旺 (peak) | 相 (supporting) | 休 (resting) | 囚 (imprisoned) | 死 (dead).
# JANGAN compute dari bulan_branch + 5-element seasonal pattern. JANGAN derive sendiri.
# Kalau seluruh kolom 體相 tidak ada di foto → semua 5 fields null.
- ti_xiang_mu: {旺/相/休/囚/死 atau null}    # status Kayu (木)
- ti_xiang_huo: {旺/相/休/囚/死 atau null}   # status Api (火)
- ti_xiang_tu: {旺/相/休/囚/死 atau null}    # status Tanah (土)
- ti_xiang_jin: {旺/相/休/囚/死 atau null}   # status Logam (金)
- ti_xiang_shui: {旺/相/休/囚/死 atau null}  # status Air (水)
- format: {format Hanzi 3 karakter terbaca eksplisit dari foto, mis. 偏財格 — null kalau tidak terbaca}
- format_label_id: {OPTIONAL — Indonesian label kustom format, mis. "Kritikus Tajam" untuk 傷官格. Null kalau pakai default engine table.}
- dm_label_id: {OPTIONAL — Indonesian label kustom day master, mis. "Api Lilin" untuk 丁火 atau "Pohon Besar" untuk 甲木. Null kalau pakai default engine table.}
- da_yun: {umur:stem branch:ten_god, ...}    # FORMAT KAYA (rekomendasi): "10:乙未:正官, 20:甲午:偏印, 30:癸巳:傷官, ...". Ten god dari foto NCC main BaZi grid baris 大運 (label di atas tiap cycle stem). Kalau foto ten_god tidak terbaca → jatuhkan suffix `:ten_god`, format simpel: "10:乙未, 20:甲午, ..." — engine akan fallback ke mapping deterministic 5-element.
- marriage_cocok: {cabang Hanzi dari layar 婚配, mis. 子, 申, 酉 — JANGAN derive dari day branch. Jumlah ikut foto persis (bisa 2/3/4/5).}
- marriage_hindari: {cabang Hanzi dari layar 婚配, mis. 丑, 卯, 辰, 戌 — JANGAN derive dari day branch. Jumlah ikut foto persis.}

# Marriage relationship label per branch — ONLY kalau foto layar 婚配 group/categorize cocok-hindari ke 三合/六合/六沖/六害/三刑.
# Format: "{branch}:{label_hz}" dipisah koma. Label valid: 三合, 六合, 六沖, 六害, 三刑, 破.
# Kalau foto cuma list flat tanpa kategori → null. Engine TIDAK derive label sendiri (FULL-MD strict).
- marriage_cocok_relationships: {mis. "子:三合, 申:三合, 酉:六合" atau null kalau foto tidak group}
- marriage_hindari_relationships: {mis. "丑:六害, 卯:六沖, 辰:三刑, 戌:破" atau null}
- yang_zhai_gua: {1 hanzi gua TERBACA EKSPLISIT dari label foto layar 陽宅 (biasanya baris 1 "○震卦" atau "○離卦"). JANGAN derive sendiri dari deskripsi hunian (mis. "menghadap utara"). Null kalau label tidak terbaca. Engine TIDAK derive Ba Zhai sendiri.}
- ziwei_ming_zhu: {2 hanzi, mis. 祿存}
- ziwei_shen_zhu: {2 hanzi, mis. 天相}
- ziwei_ming_gong: {1 hanzi cabang, mis. 寅}
- ziwei_shen_gong: {1 hanzi cabang, mis. 寅}
- ziwei_wu_xing_ju: {3 hanzi, mis. 木三局}
- ziwei_shi_jun: {1 hanzi cabang, mis. 子}

# === FULL-MD MODE FIELDS (V4.5 NO engine compute) ===
# Semua dari layar 批命備註 (skor 旺度 + DM strength). Null jika foto tidak ada.
- wangdu_jia_mu: {skor 甲木 atau null}
- wangdu_yi_mu: {skor 乙木 atau null}
- wangdu_bing_huo: {skor 丙火 atau null}
- wangdu_ding_huo: {skor 丁火 atau null}
- wangdu_wu_tu: {skor 戊土 atau null}
- wangdu_ji_tu: {skor 己土 atau null}
- wangdu_geng_jin: {skor 庚金 atau null}
- wangdu_xin_jin: {skor 辛金 atau null}
- wangdu_ren_shui: {skor 壬水 atau null}
- wangdu_gui_shui: {skor 癸水 atau null}
- wangdu_total_mu: {木 total atau null}
- wangdu_total_huo: {火 total atau null}
- wangdu_total_tu: {土 total atau null}
- wangdu_total_jin: {金 total atau null}
- wangdu_total_shui: {水 total atau null}
- dm_pos_score: {主旺 score atau null}
- dm_neg_score: {主衰 score atau null}
- dm_strength: {旺 / 弱 / 平 atau null}
- dm_strength_label_id: {Kuat / Lemah / Seimbang atau null}

# Da Yun arah & start age (dari grid BaZi utama)
- da_yun_arah: {順行 atau 逆行 atau null}
- da_yun_start_age: {umur cycle 1, harus sama dengan angka pertama di field `da_yun`}

# Shen Sha eksplisit dari foto layar 神煞 (pakai @pilar)
- shen_sha_list: {contoh "天乙貴人@日, 文昌@月, 驛馬@時" atau null}

# Na Yin per pilar (opsional, dari foto)
- nayin_tahun: {atau null}
- nayin_bulan: {atau null}
- nayin_hari: {atau null}
- nayin_jam: {atau null}

# Hidden stems / 藏干 per pilar (opsional, dari foto)
- canggan_tahun: {1-3 hanzi atau null}
- canggan_bulan: {1-3 hanzi atau null}
- canggan_hari: {1-3 hanzi atau null}
- canggan_jam: {1-3 hanzi atau null}

# ============================================================================
# V7 PAGE 04 ENRICHMENT — fields RENDERED di PDF V7 Page 04 (Profil & 4 Pilar)
# Foto-first strict. Kalau foto tidak ada → null = block hidden gracefully.
# ============================================================================

# 藏干 + 十神 per pilar — hidden stems dengan label ten god
# 🚨 STRICT FOTO-ONLY — DILARANG COMPUTE / DERIVE 🚨
#   Ten god per hidden stem WAJIB terbaca eksplisit dari foto sebagai label di samping
#   hidden stem (mis. foto kasih "戊偏官 乙傷官 癸劫財" di bawah branch 辰).
#   JANGAN compute pakai rumus polaritas + 5-element relation ke day master.
#   Kalau foto tidak tampilkan label ten god per hidden stem → SEMUA 4 field null.
# Sumber: foto Main BaZi grid baris di bawah branch tiap pilar.
# Format: "stem:ten_god" dipisah koma. Mis. "戊:偏官, 乙:偏印, 癸:比肩"
- canggan_shi_shen_tahun: {format "stem:ten_god, ..." atau null}
- canggan_shi_shen_bulan: {sama format atau null}
- canggan_shi_shen_hari: {sama format atau null}
- canggan_shi_shen_jam: {sama format atau null}

# 12 長生 phase per pilar — siklus kekuatan kontekstual
# 🚨 STRICT FOTO-ONLY — DILARANG COMPUTE / DERIVE 🚨
#   Phase WAJIB terbaca eksplisit dari foto sebagai label hanzi (帝旺/長生/dll).
#   JANGAN lookup standard table (mis. 壬水 di 子 = 帝旺) — itu compute layer.
#   Kalau foto tidak tampilkan phase label → SEMUA 4 field null.
# Sumber: foto Main BaZi grid baris di bawah branch tiap pilar (di samping/atas 藏干).
# Valid 12 phase: 長生 / 沐浴 / 冠帶 / 臨官 / 帝旺 / 衰 / 病 / 死 / 墓 / 絕 / 胎 / 養
- chang_sheng_tahun: {1-2 hanzi phase atau null}
- chang_sheng_bulan: {1-2 hanzi phase atau null}
- chang_sheng_hari: {1-2 hanzi phase atau null}
- chang_sheng_jam: {1-2 hanzi phase atau null}

# 空亡 (Kong Wang) — 2 cabang yang "kosong"
# 🚨 STRICT FOTO-ONLY — DILARANG COMPUTE / DERIVE 🚨
#   WAJIB terbaca eksplisit di foto (label "空亡: 申 酉" atau di sub-section 神煞).
#   JANGAN compute pakai 60甲子 day pillar lookup.
#   Kalau foto tidak label → null.
# Sumber: foto Main BaZi grid (biasanya bawah grid atau di kolom 神煞 sub-section).
# Format: 2 hanzi cabang dipisah koma. Mis. "申, 酉".
- kong_wang: {2 hanzi cabang dipisah koma atau null}

# === 八字秤骨 (BaZi Bone Weighing) — dari layar 先天論命 → 八字秤骨 (NCC software) ===
# Layar 八字秤骨 menampilkan:
#   - 4 berat per pilar (mis. "甲辰年: 八錢", "己巳月: 九錢", "壬戌日: 一兩", "庚子日: 一兩六錢")
#   - Total/秤骨輕重 (mis. "四兩三錢")
#   - Puisi 4-baris (詩曰: ...) yang merangkum nasib subjek
# Foto-first strict: kutip persis dari foto. Puisi parafrase Indonesia BOLEH (4 baris,
#   makna ringkas, tidak nambah info di luar foto).
- bone_weight_year: {berat tahun, mis. "八錢" atau "1兩6錢" — null kalau tidak ada}
- bone_weight_month: {berat bulan, mis. "九錢" — null}
- bone_weight_day: {berat hari, mis. "一兩" — null}
- bone_weight_hour: {berat jam, mis. "一兩六錢" — null}
- bone_weight_total: {total Hanzi, mis. "四兩三錢" — null}
- bone_weight_poem_hz: {puisi 4 baris Hanzi original, dipisah `\n` per baris.
  Mis. "為人心性最聰明\n作事軒昂近貴人\n衣祿一生天數定\n不須勞碌是豐享" — null}
- bone_weight_poem_id: {parafrase Indonesia 4 baris (atau prosa pendek 25-40 kata).
  HARUS sesuai isi puisi Hanzi — JANGAN tambah interpretasi di luar foto. Null kalau hz null}

## TAFSIR

### Kepribadian
<!-- Section ini punya 6 sub-blok. PARAGRAF wajib diisi.
     Sub-blok lain (radar_traits/motto/power/shadow/optimum): kalau confidence Anda TINGGI
     (data terbaca jelas dari foto atau interpretasi standar BaZi yakin), isi lengkap.
     Kalau confidence RENDAH atau ragu → tulis seluruh sub-blok = `null`. Engine akan
     fallback ke template per-stem (戊→Gunung/dll). LEBIH BAIK null daripada salah. -->

paragraf: <!-- 60-90 kata. Inti karakter berdasarkan day master + format + posisi cabang. -->
(tulis di sini)

radar_traits: <!-- 6 axis trait + skor 0-10. WAJIB tepat 6 axis. Total skor idealnya 35-50.
                  Confidence rendah → tulis `null` (seluruh radar_traits). -->
- {Hanzi 1-2 char} / {Pinyin} / {Label Indo}: {skor 0-10}
- (5 baris lagi sesuai pola di atas)

motto: <!-- Arketipe simbolik. Per-stem default tersedia di engine, jadi kalau ragu pakai null.
            Confidence rendah → tulis `motto: null` (skip block ini). -->
- hanzi: {1 hanzi, mis. 山}
- nama: {Nama Indo, max 3 kata}
- archetype: {4 hanzi, mis. 本性 厚重}
- tag: {4 hanzi pegangan, mis. 厚德載物}

power: <!-- Kekuatan unik subjek ini (BUKAN generic per stem). 4 bullet, MAX 18 kata.
            Kalau Anda cuma bisa generic (no foto/no context), tulis `power: null`. -->
- {bullet 1}
- {bullet 2}
- {bullet 3}
- {bullet 4}

shadow: <!-- Sisi gelap unik subjek ini. 4 bullet, MAX 18 kata. Null kalau ragu. -->
- {bullet 1}
- {bullet 2}
- {bullet 3}
- {bullet 4}

optimum: <!-- Cara optimal subjek ini. 4 bullet, MAX 18 kata. Null kalau ragu. -->
- {bullet 1}
- {bullet 2}
- {bullet 3}
- {bullet 4}

### Kepribadian Detail
<!-- Halaman "Kepribadian Detail" (性情). Sumber: foto layar 【性情】 (biasanya 2-4 baris berawalan ◎).
     WAJIB diisi kalau foto 性情 ada — kalau tidak, halaman auto-skip (jangan halusinasi).
     Format: 1 bullet `- ` per poin ◎ di foto (jumlah ikut foto). Terjemah PENUH + parafrase
     profesional + inline [[hanzi]] istilah kunci. `action:` = 1 kalimat inti watak. FOTO-STRICT. -->
poin:
- {poin ◎ pertama dari foto 性情, terjemah penuh + [[hanzi]]}
- {poin ◎ kedua}
- {poin ◎ ketiga, dst sesuai jumlah ◎ di foto}
action: {1 kalimat ringkas inti watak diri}

### Sekilas Hidup
<!-- Halaman "Sekilas Hidup" (全局總論). Sumber: foto layar 【全局總論】 (daftar kalimat ringkas
     soal pasangan/anak/ortu/sikap diri). WAJIB diisi kalau foto 全局總論 ada — kalau tidak, auto-skip.
     Format: 1 bullet `- ` per kalimat foto = "Label | teks". Label = topik singkat (mis. Pasangan,
     Anak, Hubungan dgn Ibu). Jumlah kartu ikut foto persis (no fabrikasi). `action:` = pesan inti. -->
card:
- {Label} | {teks dari kalimat foto 全局總論 + [[hanzi]] kunci}
- {Label} | {teks kalimat berikutnya, dst sesuai jumlah kalimat di foto}
action: {1 kalimat pesan inti hubungan terdekat & sikap diri}

### Keluarga & Pasangan
<!-- 4 kartu interpretasi keluarga. Tiap kartu wajib personal per subjek (BUKAN generic).
     Confidence rendah → null per kartu (engine kosongkan kartu).
     STRICT: "body" tiap kartu MAX 55 kata. Lebih dari itu = overflow di PDF. RINGKAS.
     Total seluruh family section (4 body) MAX 220 kata. -->

pasangan:
- vibe: {2-3 kata, mis. "Cerdas · Suportif"}
- headline: {1 kalimat ringkas, max 12 kata}
- body: {40-55 kata STRICT, sifat pasangan ideal & dinamika. Overflow PDF kalau lebih.}

anak:
- vibe: {2-3 kata}
- headline: {1 kalimat ringkas, max 12 kata}
- body: {40-55 kata STRICT, hubungan dengan anak & pola pengasuhan. Overflow PDF kalau lebih.}

saudara:
- vibe: {2-3 kata}
- headline: {1 kalimat ringkas, max 12 kata, WAJIB tentang saudara kandung — JANGAN sebut sahabat/teman/rekan}
- body: {40-55 kata STRICT, KHUSUS relasi SAUDARA KANDUNG (kakak/adik) saja. Overflow PDF kalau lebih. JANGAN dialihkan ke "sahabat" atau "teman" — itu masuk kepemimpinan/karir di section lain. Kalau MD tidak ada info eksplisit di foto, gunakan interpretasi BaZi standar tentang relasi saudara kandung berdasarkan istana 兄弟宮.}

kepemimpinan:
- vibe: {2-3 kata}
- headline: {1 kalimat ringkas, max 12 kata}
- body: {40-55 kata STRICT, gaya kepemimpinan & kewenangan. Overflow PDF kalau lebih.}

### Shen Sha (Bintang Pelengkap)

paragraf: <!-- 60-90 kata. Inti shen sha + interpretasi. -->
(tulis di sini)

dominant_star: <!-- Bintang dominan dari foto Xing Qiao (yang paling AKTIF). Confidence rendah → null. -->
- hanzi: {1-2 hanzi, mis. 驛馬 / 桃花 / 天乙 / 文昌}
- pinyin: {Yì Mǎ / Táo Huā / Tiān Yǐ / Wén Chāng}
- label_id: {nama Indo, mis. "Bintang Perpindahan"}
- active_label: {"AKTIF SEKARANG" atau "DORMANT"}

strip: <!-- Saran ringkas terkait shen sha aktif. Max 30 kata. Confidence rendah → null. -->
{1-2 kalimat ringkas}

### Rezeki & Caifu

paragraf: <!-- 60-90 kata. Pola finansial. -->
(tulis di sini)

zheng_cai: <!-- Rezeki tetap (gaji/rutin). Confidence rendah → null. -->
- label: "Rezeki Tetap"
- percent: {persentase porsi, 0-100%, mis. "60%". WAJIB: zheng + pian total 100%.}
- body: {40-60 kata. WAJIB konsisten dengan percent — kalau percent rendah, body bilang "porsi kecil/minoritas/bukan saluran utama"; kalau percent tinggi, body bilang "porsi besar/dominan/saluran utama". JANGAN sebut "stabil" kalau percent < 50%.}

pian_cai: <!-- Rezeki tak terduga (proyek/spekulatif). Total zheng+pian = 100%. -->
- label: "Rezeki Tak Terduga"
- percent: {persentase porsi, total zheng+pian = 100%}
- body: {40-60 kata, konsisten dengan percent (lihat aturan di zheng_cai)}

rules: <!-- 4 aturan emas mengelola rezeki. Tone "tip" (hijau positif) atau "warn" (merah peringatan). Tiap rule null jika ragu. -->
- title: {max 12 kata}; context: {max 25 kata}; tone: {tip/warn}
- title: ...; context: ...; tone: ...
- title: ...; context: ...; tone: ...
- title: ...; context: ...; tone: ...

### Karir & Industri

intro: <!-- 40-60 kata, intro karir. -->
(tulis di sini)

tags: <!-- 4 tag elemen (2 mendukung 水/木 fav, 2 hindari 金/土 unfav). Sesuaikan dengan yong/ji shen subjek. -->
- fav_1: hz: {1 hanzi unsur}; label: {label Indo singkat, mis. "ALIRAN"}
- fav_2: hz: ...; label: ...
- unfav_1: hz: ...; label: ...
- unfav_2: hz: ...; label: ...

industri: <!-- 5 industri PALING SEARAH dari foto 事業 layar.
WAJIB:
- Ambil 5 dari list profesi yang foto sebut langsung (mis. 律師/Pengacara, 醫師/Dokter, 音樂家/Musisi, 會計/Akuntansi, 金融界/Keuangan, 機械/Mesin, dll).
- JANGAN fabricate bidang berdasarkan yong_shen logic (mis. "Pendidikan & Pelatihan" cuma karena yong=木 — itu interpretasi BaZi, BUKAN dari foto).
- Kalau foto 事業 tampilkan ~28 profesi, pilih 5 paling representatif (kombinasi favorable + supportive).
- Field `alasan`: kalau foto tidak punya tafsir spesifik per profesi, tulis ringkas seperti "foto 事業 sebut langsung sebagai bidang searah". JANGAN ngarang alasan personal subjek.
Format per baris: nama (Hanzi/Indo); unsur (1 hanzi); alasan (max 18 kata, foto-grounded). -->
- nama: {profesi 1, format "[[Hanzi]] / Indo"}; unsur: {hz}; alasan: {foto-grounded, max 18 kata}
- nama: ...
- nama: ...
- nama: ...
- nama: ...

### Day Master & Wu Xing
<!-- 2 sub-field. paragraf: 40-60 kata, bahas DM + 用神/喜用神 (positif). ji_shen_body: 30-50 kata, bahas 忌神/仇神 (yang dihindari). Section ini render ke 2 kartu di page 6: paragraf → kartu DIRI/MENDUKUNG (atas), ji_shen_body → kartu KURANG MENDUKUNG (bawah). -->

paragraf: <!-- 40-60 kata. DM elemen + status (lemah/kuat) + 用神 utama + 喜用神 pendukung. -->
(tulis di sini)

ji_shen_body: <!-- 30-50 kata. 忌神 + 仇神 yang harus dihindari + dampaknya. -->
(tulis di sini)

### Yang Zhai (Feng Shui Hunian)

paragraf: <!-- 60-90 kata. Trigram pribadi + arah hoki + saran tata letak. -->
(tulis di sini)

zones: <!-- 6 zone hunian/ruang. Tiap zone: { label, headline (✓/⚠ + 1 frase), pills (1-2 arah Hanzi), note (max 18 kata) }. Confidence rendah → null per zone. -->
- label: "Pintu Utama"; headline: "✓ Optimal"; pills: {Hanzi arah, mis. 東 T}; note: {max 18 kata}
- label: "Kamar Tidur"; headline: ...; pills: ...; note: ...
- label: "Dapur / Kompor"; headline: ...; pills: ...; note: ...
- label: "Kamar Mandi"; headline: ...; pills: ...; note: ...
- label: "Ruang Kerja"; headline: ...; pills: ...; note: ...
- label: "Altar / Sembah"; headline: ...; pills: ...; note: ...

### Da Yun — Spotlight (Fase Sekarang)
<!-- Headline RINGKAS, MAX 15 kata (lebih pendek lebih baik). Format yang dianjurkan:
     "Fase X–Y: {Indonesia} ([[gz]]), {2-4 kata kunci esensi fase}". Contoh: "Fase 59–68: Kayu Yin Kerbau ([[乙丑]]), Konsolidasi Sebelum Panen".
     Bullet: 4 bullet @ MAX 25 kata STRICT. Layout PDF tidak akomodasi bullet panjang. -->

headline: (tulis di sini, MAX 15 kata)

bullet 1: (tulis di sini, MAX 25 kata)
bullet 2: (tulis di sini, MAX 25 kata)
bullet 3: (tulis di sini, MAX 25 kata)
bullet 4: (tulis di sini, MAX 25 kata)

### Da Yun — 5 Seasons
<!-- Budget: 5 baris. Tiap baris: "umur X-Y: nama_season_indo — 1 kalimat 10-15 kata". Pecah hidup ke 5 musim besar berdasarkan da yun grid di DATA. -->

- umur {a}-{b}: {nama} — {1 kalimat}
- umur {c}-{d}: {nama} — {1 kalimat}
- umur {e}-{f}: {nama} — {1 kalimat}
- umur {g}-{h}: {nama} — {1 kalimat}
- umur {i}-{j}: {nama} — {1 kalimat}

### Da Yun — Footer Caption
<!-- 1 baris pendek, MAX 25 kata. Muncul di footer halaman intro (page 3).
     Format: "{Nama} di fase [[gz]] (X-Y) — {esensi 1 frase singkat}".
     JANGAN tambah klausa panjang ekstra. -->

(tulis di sini, MAX 25 kata)

### Palace Detail 1
<!-- 4 palace pertama: 命宮/兄弟/夫妻/子女. Tiap palace: { star (1-2 hanzi main star), insight (50-70 kata), action (1 baris max 18 kata) }. Confidence rendah → null per palace.

WARNING: Zi Wei chart foto sangat padat (12 cell × 5-15 stars per cell). Common bug: pilih bintang yang BUKAN main star (mis. confused antara main star dan minor star). Cara baca yang benar:
1. Identifikasi cabang istana (mis. 巳, 辰, 卯, dll) di pojok cell
2. Main star biasanya di baris pertama cell, font lebih besar / warna khusus (kuning/hijau/merah)
3. Modifier 廟/旺/得/平/陷 melekat di main star (mis. 紫微旺, 廉貞陷)
4. Minor stars (祿存, 文昌, 文曲, 紅鸞, 天喜, 將星, 白虎, etc.) ada di bawah, JANGAN dipilih sebagai main
5. Kalau cell hanya berisi minor stars (no major), tulis `star: null` — JANGAN paksa pilih
6. Cross-check: jumlah 14 main stars (紫微/天機/太陽/武曲/天同/廉貞/天府/太陰/貪狼/巨門/天相/天梁/七殺/破軍) per chart Zi Wei — masing-masing main star muncul di SATU palace saja (kecuali doublestar 紫微+破軍 di 紫破 palace). Kalau Anda assign main star yang sama ke 2 palace berbeda → salah satu salah. -->

ming_gong: <!-- Istana Hidup -->
- star: {hanzi main star 1-2 karakter, mis. 紫微 / 天府 / 太陰. KALAU FOTO TIDAK ADA bintang utama yang terbaca, tulis null. Engine akan tampilkan "—" + label "tidak terbaca". JANGAN tebak.}
- insight: {50-70 kata}
- action: {max 18 kata}

xiongdi: <!-- Istana Saudara -->
- star: ...
- insight: ...
- action: ...

fuqi: <!-- Istana Pasangan -->
- star: ...
- insight: ...
- action: ...

zinu: <!-- Istana Anak -->
- star: ...
- insight: ...
- action: ...

### Palace Detail 2
<!-- 4 palace tengah: 財帛/疾厄/遷移/僕役. Sama struktur dengan Palace Detail 1. -->

caibo: <!-- Istana Rezeki -->
- star: ...
- insight: {50-70 kata}
- action: {max 18 kata}

jie_e: <!-- Istana Kesehatan -->
- star: ...
- insight: ...
- action: ...

qianyi: <!-- Istana Perpindahan -->
- star: ...
- insight: ...
- action: ...

puyi: <!-- Istana Sahabat/Bawahan -->
- star: ...
- insight: ...
- action: ...

### Palace Detail 3
<!-- 4 palace akhir: 官祿/田宅/福德/父母. Sama struktur. -->

guanlu: <!-- Istana Karir -->
- star: ...
- insight: {50-70 kata}
- action: {max 18 kata}

tianzhai: <!-- Istana Properti -->
- star: ...
- insight: ...
- action: ...

fude: <!-- Istana Berkah -->
- star: ...
- insight: ...
- action: ...

fumu: <!-- Istana OrangTua -->
- star: ...
- insight: ...
- action: ...

### Kesimpulan
<!-- Quote 1 kalimat (25-40 kata) + 5 stat descriptions personal + 3 life_map narrative.
     Sisa stat cards (Penguasa Hari, Umur Subjek, Kompatibilitas) sudah auto rumus engine.
     KETAT budget kata, layout PDF tidak akomodasi kalimat panjang. -->

quote: "(tulis di sini, 25-40 kata)"

stats:
- format_desc: {MAX 16 kata STRICT. Bagaimana format BaZi memengaruhi karakter subjek konkret.}
- yong_desc: {MAX 16 kata STRICT. Bagaimana yong shen (unsur pendukung) sebaiknya diaktifkan sehari-hari.}
- dayun_desc: {MAX 16 kata STRICT. Tema inti fase Da Yun yang sedang dijalani.}
- umur_desc: {MAX 16 kata STRICT. Karakter dekade umur subjek saat ini.}
- kompat_desc: {MAX 16 kata STRICT. Pola relasi cocok + hindari yang perlu diingat.}

life_map:
- lalu: {MAX 30 kata. Ringkasan fase yang sudah dilewati subjek, elemen + tema utama.}
- sekarang: {MAX 30 kata. Fase saat ini + tema pemurnian/pertumbuhan/transformasi.}
- berikutnya: {MAX 30 kata. Preview fase mendatang, ke mana arah, transisi seperti apa.}

### Sintesis & Saran Aksi
<!-- Opening + 3 trio cards (Kekuatan/Tantangan/Tindakan) + 5 actions list. Mantra DIHAPUS dari template, jangan diisi. -->

opening: <!-- 1 kalimat 25-35 kata, ringkas siapa subjek ini. -->
(tulis di sini)

trio: <!-- 3 kartu fundamental. Tiap kartu WAJIB: hanzi 2-3 hanzi + pinyin + arti (Indonesia, max 5 kata) + body 40-60 kata. WAJIB sertakan `arti` karena user TIDAK BISA BACA HANZI. Confidence rendah → null per kartu. -->

kekuatan:
- hanzi: {2-3 hanzi, mis. 魄力 / 才華}
- pinyin: {Pò Lì / Cái Huá}
- arti: {arti Indonesia ringkas, max 5 kata, mis. "Tekad yang Membaja"}
- body: {40-60 kata, kekuatan inti subjek}

tantangan:
- hanzi: {2-3 hanzi, mis. 考驗 / 挑戰}
- pinyin: ...
- arti: {arti Indonesia, max 5 kata}
- body: {40-60 kata, tantangan utama}

tindakan:
- hanzi: {2-3 hanzi, mis. 作為 / 行動}
- pinyin: ...
- arti: {arti Indonesia, max 5 kata}
- body: {40-60 kata, panggung optimal}

actions: <!-- 5 saran aksi praktis. Tiap baris: title (max 12 kata) + context (max 18 kata). TIDAK ADA tag elemen. -->
- title: ...; context: ...
- title: ...; context: ...
- title: ...; context: ...
- title: ...; context: ...
- title: ...; context: ...

## CATATAN

<!-- Tulis catatan tentang field yang null (tidak terbaca dari foto), atau field interpretatif yang Anda isi sendiri (bukan dari foto). Format bebas, untuk audit user. -->

(tulis catatan di sini, atau "Tidak ada — semua field terbaca dari foto.")

## DATA_EXTRA

<!--
============================================================================
PENTING — BACA SEBELUM MENGISI:

1. Section ini = ARSIP. Berisi data yang TERBACA di foto Xing Qiao tapi
   BELUM dipakai di template PDF V4.5 saat ini.

2. Engine `parse_md.py` SKIP section ini saat build PDF — TIDAK akan
   menyebabkan error/crash. Field di sini tidak muncul di PDF.

3. Tujuan: arsip data lengkap + future-proofing kalau template PDF nanti
   di-update untuk menampilkan field-field ini.

4. WAJIB diisi tetap kalau fotonya ada — supaya data tidak hilang
   walaupun belum ke-render. JANGAN dipindah ke section ## DATA atau
   ## TAFSIR — engine tidak handle field-field ini di sana.

5. Kalau foto-fotonya tidak ada → semua field null. Tidak masalah.
============================================================================
-->

### 仇神 (Chou Shen / Musuh Netral) — dari layar 用神/忌神/批命備註
<!-- Software biasanya tampilkan trio: 用神 / 忌神 / 仇神 (kadang + 喜神 + 閒神).
     仇神 = elemen yang menetralkan/melawan yong shen. Baca eksplisit dari foto. -->

- chou_shen: {1-2 elemen Hanzi terbaca eksplisit, mis. 土 — null kalau foto tidak ada label}
- xi_shen: {1-2 elemen Hanzi 喜神 (jika ada), mis. 火 — null jika foto tidak ada}
- xian_shen: {1-2 elemen Hanzi 閒神 (jika ada), mis. 金 — null jika foto tidak ada}

### 先天體檢 per organ — dari layar 先天體檢 (kolom kanan)
<!-- Layar 先天體檢 biasanya tampilkan mapping stem → organ tubuh (TCM:
     甲膽 乙肝 丙小腸 丁心 戊胃 己脾 庚大腸 辛肺 壬膀胱 癸腎).
     Angka di samping = count dari xiantian_* (sudah di DATA section).
     Tulis nama organ Hanzi-nya di sini supaya arsip lengkap. -->

- xiantian_organ_jia: {hanzi organ, mis. 膽 — null kalau tidak terbaca}
- xiantian_organ_yi: {肝}
- xiantian_organ_bing: {小腸}
- xiantian_organ_ding: {心}
- xiantian_organ_wu: {胃}
- xiantian_organ_ji: {脾}
- xiantian_organ_geng: {大腸}
- xiantian_organ_xin: {肺}
- xiantian_organ_ren: {膀胱}
- xiantian_organ_gui: {腎}
- xiantian_organ_health_notes: {string bebas, max 60 kata. Mis. "甲1膽 normal, 己0脾 sangat lemah, 辛0肺 lemah — perlu perhatikan organ-organ ini." Null kalau ragu.}

### Da Yun start age — string detail dari foto
<!-- Selain `da_yun_start_age` (angka) di DATA section, software kadang tampilkan
     keterangan kapan persis da yun mulai dengan format "每逢後X或Y年..." — tulis
     string aslinya di sini sebagai arsip. -->

- da_yun_start_note_hz: {string Hanzi original dari foto, mis. "每逢後8或11年個小月滿又後27天交大運" — null kalau tidak terbaca}
- da_yun_start_note_id: {terjemahan Indonesia ringkas 1-2 kalimat, mis. "Da Yun mulai 8 tahun setelah lahir, transisi tepat pada tanggal X" — null kalau hz null}

### 古書云 — kutipan klasik tentang Day Master
<!-- Layar 古書云 menampilkan puisi/kutipan kitab kuno tentang day master subjek
     (mis. tentang 丁火 untuk DM 丁). Kutip apa adanya + terjemahan ringkas. -->

- gushuyun_paragraf_hz: {kutipan Hanzi original 1-3 kalimat dari foto, max 80 karakter Hanzi — null kalau foto tidak ada}
- gushuyun_terjemahan_id: {terjemahan Indonesia ringkas 1-2 kalimat, max 50 kata — null kalau hz null}

### 全局總論 — ringkasan keseluruhan dari layar 全局總論
<!-- Software tampilkan summary global tentang chart subjek (配偶名氣, 兒子聰明,
     母親話有威信, dll). Kutip ringkas. -->

- quan_ju_paragraf: {kutipan parafrase Indonesia max 100 kata dari foto layar 全局總論. Null kalau foto tidak ada.}
- quan_ju_bullets: <!-- 3-6 poin highlight dari layar, kalau ada bullet/poin terpisah. Null kalau tidak ada. -->
  - {poin 1, max 18 kata}
  - {poin 2, max 18 kata}
  - {poin 3, max 18 kata}

### 父母 BaZi (BUKAN versi Zi Wei) — dari layar 父母 di software BaZi
<!-- Software punya layar 父母 versi BaZi (analisis hubungan ortu via 4 pilar)
     yang BERBEDA dari 父母宮 di Zi Wei. Tulis kutipan ringkas dari layar BaZi. -->

- fumu_bazi_paragraf: {kutipan parafrase Indonesia max 80 kata dari layar 父母 BaZi. Null kalau foto tidak ada.}

### 事業 (Karir BaZi) — kutipan langsung dari layar 事業
<!-- Layar 事業 software tampilkan bidang karir spesifik (BUKAN interpretasi).
     Tulis ringkasan + label kelompok karir yang software sebutkan. -->

- shiye_paragraf: {kutipan parafrase Indonesia max 80 kata dari layar 事業. Null kalau foto tidak ada.}
- shiye_industri_kelompok: {label kelompok karir yang software sebutkan, kutip persis. Mis. "教育 / 文化 / 出版 (Pendidikan, Budaya, Penerbitan)" — null kalau tidak ada.}

### 性情 (Personality detail) — kutipan dari layar 性情
<!-- Layar 性情 / 性格 software tampilkan deskripsi kepribadian detail.
     Walaupun ada `kepribadian.paragraf` di TAFSIR, kutipan original dari foto
     biasanya lebih kaya. Tulis di sini sebagai arsip lengkap. -->

- xing_qing_paragraf: {kutipan parafrase Indonesia max 120 kata dari layar 性情. Null kalau foto tidak ada.}

### 流年易鑑 — Tabel multi-usia (dari foto layar 流年易鑑)
<!-- Tabel per usia dengan kolom: usia, ganzhi, ten god, shen sha utama,
     shen sha minor. Biasanya cover usia X-Y (mis. 30-49). Tulis SEMUA
     baris yang terbaca. Format per baris: usia/ganzhi/ten_god/shen_sha_main/shen_sha_minor. -->

- liu_nian_table: <!-- list per usia. Null kalau foto tidak ada. -->
  - usia {N}: ganzhi {hz}; ten_god {hz}; shen_sha_main {hz}; shen_sha_minor {hz}
  - usia {N+1}: ...
  - (sampai usia max yang terbaca di foto)

### 流年判斷 — Prediksi tafsir per tahun
<!-- Foto layar 流年 sering punya tafsir prediksi 5 tahun ke depan dari current.
     Kutip parafrase ringkas per tahun. Sertakan tahun gregorian + usia + ganzhi. -->

- liu_nian_predictions: <!-- 5 entri tahun ke depan. Null kalau foto tidak ada. -->
  - tahun {YYYY} (usia {N}, [[ganzhi_hz]]): {tafsir parafrase Indonesia 30-50 kata}
  - tahun {YYYY+1} (usia {N+1}, [[ganzhi_hz]]): ...
  - tahun {YYYY+2} ...
  - tahun {YYYY+3} ...
  - tahun {YYYY+4} ...

### Bintang Zi Wei lengkap per palace
<!-- Software Zi Wei tampilkan banyak bintang minor per palace selain bintang utama.
     Field `ziwei_*_zhu` di DATA hanya catat main star — di sini tulis SEMUA bintang
     yang terbaca per palace, dipisah koma. -->

- ziwei_stars_ming: {SEMUA bintang di 命宮, mis. "武曲, 天府, 文昌, 文曲, 紅鸞, 天哭" — null kalau palace tidak terbaca}
- ziwei_stars_xiongdi: {di 兄弟宮 atau null}
- ziwei_stars_fuqi: {di 夫妻宮 atau null}
- ziwei_stars_zinu: {di 子女宮 atau null}
- ziwei_stars_caibo: {di 財帛宮 atau null}
- ziwei_stars_jie_e: {di 疾厄宮 atau null}
- ziwei_stars_qianyi: {di 遷移宮 atau null}
- ziwei_stars_puyi: {di 僕役宮 atau null}
- ziwei_stars_guanlu: {di 官祿宮 atau null}
- ziwei_stars_tianzhai: {di 田宅宮 atau null}
- ziwei_stars_fude: {di 福德宮 atau null}
- ziwei_stars_fumu: {di 父母宮 atau null}

### Score BaZi raw format (kalau pakai desimal)
<!-- Sebagian software tampilkan score dengan desimal (mis. +3.678 / -5.102) bukan
     integer. Kalau format yang terbaca beda dari `dm_pos_score`/`dm_neg_score` di
     DATA (yang ekspektasi integer), tulis string original di sini sebagai backup. -->

- dm_score_raw: {string angka original dari foto, mis. "+3.678 / -5.102" — null kalau dm_pos_score sudah integer}

### Tafsir tambahan dari foto layar lain
<!-- Layar2 lain di software (mis. 財帛, 配偶, 子女) yang punya kutipan/tafsir
     yang TIDAK ke-cover di TAFSIR section di atas. Tulis ringkas per layar. -->

- tafsir_layar_lain: <!-- Format: list "{nama layar hz}: {kutipan parafrase Indonesia max 60 kata}". Null kalau tidak ada. -->
  - {nama layar hz}: {kutipan parafrase}
  - {layar berikutnya}: ...

### 體相 — 5-Element Status (旺相休囚死) — DEPRECATED (moved to DATA)
<!-- Field `ti_xiang_*` 5-fields per element sudah pindah ke section ## DATA (line ~310).
     Field render ke badge lingkaran di Page 6 dme-card. -->

(Lihat ti_xiang_mu/huo/tu/jin/shui di ## DATA section.)

### 十神 per Pilar — Label Ten God Atas Tiap Stem
<!-- Layar Main BaZi grid baris atas tiap pilar tampilkan label ten god
     (傷官/比肩/偏官/正財/dst). Day pillar = 主 (subject sendiri). -->

- shi_shen_per_pilar:
  - tahun: {ten god hanzi 1-2 char, mis. 偏官 — null kalau tidak terbaca}
  - bulan: {ten god hanzi}
  - hari: {主 (default, day pillar = self)}
  - jam: {ten god hanzi}

### 藏干 + 十神 per Pilar — Hidden Stems dengan Ten God Label
<!-- Layar Main BaZi grid bawah branch tampilkan 1-3 hidden stem dengan
     ten god labels masing-masing. Format: array of {stem, ten_god}. -->

- canggan_shi_shen_tahun:
  - {stem: 戊, ten_god: 偏官}
  - {stem: 乙, ten_god: 偏印}
  - {stem: 癸, ten_god: 比肩}
- canggan_shi_shen_bulan:
  - {stem: hanzi, ten_god: hanzi}
- canggan_shi_shen_hari:
  - {stem: hanzi, ten_god: hanzi}
- canggan_shi_shen_jam:
  - {stem: hanzi, ten_god: hanzi}

### 12 長生 per Pilar — Cycle Phase
<!-- Layar Main BaZi grid bawah branch tampilkan fase 12 長生:
     長生/沐浴/冠帶/臨官/帝旺/衰/病/死/墓/絕/胎/養. Untuk subject 4 pilar. -->

- chang_sheng_per_pilar:
  - tahun: {fase hanzi 1-2 char, mis. 養 — null kalau tidak terbaca}
  - bulan: {fase hanzi}
  - hari: {fase hanzi}
  - jam: {fase hanzi}

### 命宮 dari Main BaZi Grid — Stem-Branch
<!-- Berbeda dari ziwei_ming_gong (cabang only). Main BaZi grid tampilkan
     命宮 lengkap dengan stem-branch (mis. 乙卯). Tulis full pillar. -->

- ming_gong_bazi: {stem-branch hanzi, mis. 乙卯 — null kalau tidak terbaca}

### 空亡 (Kong Wang) — Empty Branches
<!-- Beberapa software tampilkan 空亡 di main grid: branches yang "kosong"
     berdasarkan day pillar. Format: 2 cabang dipisah koma. -->

- kong_wang_branches: {2 hanzi cabang, mis. "申 酉" — null kalau tidak terbaca}

### Shen Sha — Upgrade List-of-Objects dengan Tafsir
<!-- Field `shen_sha_list` di section ## DATA hanya simpan nama+pilar (flat string).
     Di sini SIMPAN versi LENGKAP dengan tafsir per item dari layar 神煞.
     Foto layar 神煞 tampilkan: 驛馬 → "勞碌好動、奔波遠行..." per shen sha. -->

- shen_sha_detail: <!-- list of objects. Null kalau foto 神煞 tidak ada. -->
  - {nama_hz: 驛馬, pilar: 月, tafsir_hz: "勞碌好動、奔波遠行、多旅行運、住家及事業多變動。", tafsir_id: "Sangat aktif, sering bepergian jauh, rumah & karir banyak perubahan."}
  - {nama_hz: 劫煞, pilar: ?, tafsir_hz: "聰明敏捷、才智過人、巧於謀事。", tafsir_id: "Cerdas tangkas, kepandaian di atas rata-rata, lihai dalam strategi."}
  - {nama_hz: 孤辰, pilar: ?, tafsir_hz: "...", tafsir_id: "..."}
  - {nama_hz: 天醫, pilar: ?, tafsir_hz: "...", tafsir_id: "..."}

### 事業 — Industri Full List dari Foto
<!-- Field `industri` di TAFSIR Karir dipotong jadi 5 untuk PDF. Di sini SIMPAN
     full list dari layar 事業 (biasanya 2 kategori: favorable + supportive,
     total ~25 items). Format: kutip persis dari foto. -->

- industri_full:
  - kategori: favorable
    list_hz: [鋼鐵工廠, 五金行, 採礦, 汽車, 機械, 科學家, 律師, 歌影星, 音樂家, 武術館, 會計, 金融界]
    list_id: [Pabrik Baja, Toko Logam, Tambang, Otomotif, Mesin, Saintis, Pengacara, Selebriti, Musisi, Bela Diri, Akuntansi, Keuangan]
  - kategori: supportive
    list_hz: [流血攤頭, 運動家, 介紹中人, 醫師, 清潔隊, 記者, 護士, 導遊, 馬戲團, 航海漁業]
    list_id: [Operasi/Bedah, Atlet, Broker, Dokter, Cleaning Service, Wartawan, Perawat, Pemandu Wisata, Sirkus, Pelaut/Nelayan]

### Marriage Tafsir Raw — Konsekuensi 宜/忌 dari Foto
<!-- Layar 婚配 / 配偶 sering punya teks panjang konsekuensi pernikahan
     untuk setiap kategori 宜 (cocok) dan 忌 (hindari). Simpan raw. -->

- marriage_cocok_tafsir_hz: {raw hanzi 宜 section, mis. "締結良緣, 富貴成功, 勤儉建業, 老景倍加昌盛..." — null kalau tidak ada}
- marriage_cocok_tafsir_id: {parafrase Indonesia max 60 kata — null kalau hz null}
- marriage_hindari_tafsir_hz: {raw hanzi 忌 section, mis. "夫妻不能合和終世, 破壞別離, 家世運未通..." — null kalau tidak ada}
- marriage_hindari_tafsir_id: {parafrase Indonesia max 60 kata — null kalau hz null}
```

---

### CONTOH HANZI WRAPPING (ikut konvensi ini)

| Konteks | Salah | Benar |
|---|---|---|
| Sebut day master dalam kalimat | `Anda 辛金 cenderung tegas` | `Anda [[辛金]] cenderung tegas` |
| Sebut ten god | `fase 七殺 mendorong` | `fase [[七殺]] mendorong` |
| Sebut format | `cocok dengan 偏財格 Anda` | `cocok dengan [[偏財格]] Anda` |
| Sebut star Zi Wei | `紫微 di Istana` | `[[紫微]] di Istana` |
| Sebut elemen tunggal | `unsur 火 dominan` | `unsur [[火]] dominan` |
| Sebut shio | `shio 馬 (Kuda)` | `shio [[馬]] (Kuda)` |
| Bungkus seluruh kalimat | ❌ jangan | ❌ jangan |

---

### REMINDER FINAL

- Mulai output dengan `# {Nama}` (heading 1) di baris pertama. Tidak ada teks sebelumnya.
- Selesai output dengan section `## DATA_EXTRA`. Tidak ada teks setelahnya. (Order: DATA → TAFSIR → CATATAN → DATA_EXTRA)
- Tidak boleh ada teks "Berikut hasilnya:", "Saya sudah ekstrak:", dll. — langsung markdown saja.
- **DATA_EXTRA = arsip**, engine PDF skip section ini saat build. Tapi WAJIB diisi kalau fotonya ada — supaya data lengkap untuk future template update.
- Patuhi budget kata di setiap section.
- Konsisten antara DATA dan TAFSIR.
- Sebut nama subjek (bukan kata "Anda" terus-menerus) di sekitar 30% kalimat — biar PDF terasa personal.
- **Full-MD mode:** kalau foto `批命備註` ada, WAJIB ekstrak `wangdu_*` + `dm_*_score` + `dm_strength`. Ini source-of-truth untuk Day Master strength dan Yong/Ji shen — JANGAN biarkan null kalau fotonya ada.
- **Konsistensi DM:** kalau `dm_strength = 弱`, maka:
  - `yong_shen` WAJIB elemen yang generate / sama dengan day master (印 + 比劫). Contoh untuk 壬水 lemah → `yong_shen: 金 水`.
  - `ji_shen` = elemen yang menguras / mengontrol DM (財官 + 食傷). Contoh untuk 壬水 lemah → `ji_shen: 火 土` atau `土 木`.
  - JANGAN tulis `yong_shen: 木 金` untuk DM lemah — 木 menguras 水, kontradiktif.
- **Konsistensi DM strong:** kalau `dm_strength = 旺`, kebalikannya — yong_shen = 食傷財官, ji_shen = 印比.

Mulai sekarang.
