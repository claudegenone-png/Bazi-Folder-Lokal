# AUTORUN V13 — Engine 1-Agent (Sonnet, no-audit)

**Trigger:** `{path foto} pakai V13`
**Anti-ketukar:** echo `MODE: V13 (1-agent, no-audit)` di baris pertama. Ragu → tanya.
**Model:** Sonnet semua.

---

## Folder structure

**Root folder** (`{path}`) — berisi subfolder `data/`:
- `data/` — semua foto kecuali 3 foto yang dikirim langsung via prompt

**3 foto via prompt** (TIDAK di folder, langsung di-attach di chat oleh user):
- **BaZi grid** (4 pilar + 先天體檢 + 喜用神 + DM旺度 + Da Yun row)
- **命宮 ZiWei narrative**
- **Shio** (kalau tidak terlihat di BaZi grid, kirim screenshot terpisah)

Agent baca 3 foto dari **prompt context** (0 extra tool call) — file aslinya ada di root folder sebagai arsip, TIDAK dibaca dari file system.

> **Catatan:** Subfolder `transelate/` mungkin ada di root folder tapi **kosong** (tidak ada foto di dalamnya). Agent tidak perlu baca atau proses subfolder ini. Rename hanya dijalankan di `data/`.

---

## Pipeline

### PRE-FLIGHT — Cek foto wajib (SEBELUM apapun)

> **RETAKE TURN?** Kalau pesan user mengandung kata **"retake"** atau **"foto retake"** TANPA path folder → **LEWATI PRE-FLIGHT ini**, langsung ke [## Retake Turn](#retake-turn).

User WAJIB kirim **3 screenshot langsung di prompt** (sebagai image attachment):
- BaZi grid
- 命宮 ZiWei narrative
- Shio

Kalau salah satu dari 3 foto tidak di-attach di prompt → **STOP, ingatkan user singkat.** Jangan lanjut.

Cek juga: apakah semua 3 foto adalah subjek yang sama (nama/tanggal/shio konsisten)? Kalau beda → **STOP + tabel warning.**

---

### Step 0 — Rename

```
cd C:\Users\sukam\OneDrive\Documents\Ramalan\v13
python rename_photos_sequential.py "{photos_dir}/data"
```

Output: `data/1.jpeg .. data/N.jpeg`. Idempoten — aman re-run.
Foto di root folder = arsip, tidak di-rename dan tidak dibaca.

---

### Step 0.1 — Copy Blueprint (WAJIB SEBELUM TULIS MD)

Baca file:
```
C:\Users\sukam\OneDrive\Documents\Ramalan\v13\md_blueprint.md
```

Copy seluruh isi blueprint sebagai starting point MD subjek baru. Isi nilai dari foto — tulis `null` kalau tidak terlihat di foto.

**Konfirmasi nama subjek sebelum isi MD:** Nama dari software BaZi sering punya spasi (e.g. "BA YU"). Kalau ada spasi → tanya user satu kalimat: *"Nama ditulis '[nama dari software]' atau '[tanpa spasi]'?"* Jangan assume. Isi field `nama:` sesuai jawaban user.

Critical format dari blueprint (WAJIB hafal sebelum isi):
- `xi_yong_shen` = 喜神 — **BUKAN `xi_shen`**
- `dm_pos_score` / `dm_neg_score` = integer e.g. `4100` — **BUKAN `+4.100`**
- `liu_nian_YYYY` = `umur|ganzhi|prose` — **WAJIB dua pipe separator**
- `yang_zhai_gua` = **WAJIB diisi** kalau ada foto 陽宅
- `jie_e_palace_id` = **WAJIB di ## DATA** — TAFSIR jie_e.insight saja tidak cukup
- `format` = dari foto BaZi (食神用事 → `食神格`)

---

### Step 0.5 — Validasi folder

Scan `data/`:
1. **Foto buram/blank** → **catat nomor foto di list, JANGAN STOP** — blur handling dilakukan di Step 1 setelah baca konten
2. **Jumlah foto** → catat total, lanjut

`transelate/` subfolder → **abaikan**, kosong.

---

### Step 1 — Baca semua foto + tulis MD (inline, single agent)

**Tidak ada subagent. Tidak ada JSON intermediate. Tulis MD langsung.**

> **ANTI-COMPILE RULE:** DILARANG output teks analisis/rangkuman/laporan sebelum Write tool call pertama. Langsung baca → langsung tulis MD. Kalau context restart di tengah jalan → baca MD yang sudah ada → lanjut tulis field yang belum terisi, JANGAN laporan progress dulu.

#### Foto data/ — WAJIB pakai photo_feeder.py (structural gate)

JANGAN baca foto dari `data/` langsung. Wajib pakai feeder:

```powershell
cd C:\Users\sukam\OneDrive\Documents\Ramalan\v13
python photo_feeder.py init {id} "{photos_dir}/data"
```

Feeder menaruh **1 foto di `data/current/`**. Baca hanya dari `data/current/`.

**Loop wajib per foto:**
1. Baca `data/current/{foto}` (hanya 1 file di sana)
2. Edit MD — isi field dari foto itu
3. `python photo_feeder.py next {id}`
   - Kalau MD belum diupdate → **ERROR, wajib Edit MD dulu**
   - Kalau OK → foto berikutnya muncul di `data/current/`
4. Ulangi sampai feeder bilang "Semua foto selesai"

Kenapa: context window penuh setelah 1-2 foto. Feeder memastikan data foto langsung disimpan ke MD sebelum hilang dari context.

#### Tanggal lahir — WAJIB konversi dengan script

Foto BaZi menampilkan 農曆 (lunar), BUKAN Masehi. **DILARANG menebak atau hitung manual.**

Wajib jalankan setelah baca foto BaZi grid:
```powershell
# 民國 → Western: tahun + 1911. Contoh: 民國42 → 1953
# Bulan kabisat (閏月): pakai negatif, e.g. -4
cd C:\Users\sukam\OneDrive\Documents\Ramalan\v13
python lunar_convert.py <lunar_year> <lunar_month> <lunar_day>
```

Hasil script → isi `lahir_tanggal:` di MD. Juga tulis `lahir_tanggal_lunar:` (raw dari foto) sebagai referensi.

Kalau script error (input invalid) → tulis `lahir_tanggal: null` + catat di `## CATATAN`. JANGAN tebak.

#### RULE BAZI GRID — WAJIB baca KANAN ke KIRI

```
Kolom BaZi grid selalu: KANAN → KIRI = 年柱 / 月柱 / 日柱 / 時柱

  [ 時 ] [ 日 ] [ 月 ] [ 年 ]   ← label atas (Ten God / 十神)
  [干 4] [干 3] [干 2] [干 1]   ← stem (天干)
  [支 4] [支 3] [支 2] [支 1]   ← branch (地支)

  pilar_jam  = kolom PALING KIRI
  pilar_hari = kolom ke-2 dari kiri  (Day Master = stem kolom ini)
  pilar_bulan= kolom ke-3 dari kiri
  pilar_tahun= kolom PALING KANAN
```

Konfirmasi: label Ten God baris atas. Posisi "命主" atau label center = pilar_hari (Day Master).
Label "年" di header = pilar_tahun (paling kanan). JANGAN baca kiri ke kanan.

validate_bazi.py akan otomatis cross-check setelah MD selesai — kalau pilar salah → build ABORT.

Agent membaca dalam urutan:

1. **BaZi grid** (dari prompt context) → ekstrak pilar, 先天體檢, 喜用神, da yun, shio → jalankan `lunar_convert.py` → **Edit MD**
2. **命宮 ZiWei narrative** (dari prompt context) → terjemah PENUH → **Edit MD**
3. **`python photo_feeder.py init {id} "{photos_dir}/data"`** → mulai loop feeder
4. **Loop: baca `data/current/` → Edit MD → `photo_feeder.py next`** → ulangi per foto:

| Konten foto | Field target |
|---|---|
| ZiWei chart (12 palace + bintang) | `ziwei_*` fields, palace star per TAFSIR |
| 婚配 | `marriage_cocok` / `marriage_hindari` / `marriage_*_tafsir` |
| 陽宅 | `yang_zhai_gua` + 7 zone `yang_zhai_zone_*` |
| 神煞 | `shen_sha_list` / `shen_sha_detail_N` |
| 流年判斷 | `liu_nian_YYYY` (format `umur\|ganzhi\|prose`) |

Untuk setiap `liu_nian_YYYY`, kalimat pertama wajib dimulai dengan `Tahun YYYY...`. Pembuka antar-tahun harus bervariasi secara alami. Bila teks foto memakai struktur berulang, parafrasekan susunan kalimat Indonesianya tanpa mengurangi, menambah, atau memindahkan makna dari foto tahun tersebut.
| 古書云 | `gushu_quote_N` |
| 11 palace narratives (夫妻/子女/財帛 dst) | `palace_*_insight` di TAFSIR |
| 性情 | `### Kepribadian Detail` (`poin:` list) |
| 全局總論 | `### Sekilas Hidup` (`card:` "Label \| teks") |
| 事業 | `shiye_favorable_full` / `shiye_supportive_full` di `## DATA` — format WAJIB: `漢字\|Indonesia, 漢字\|Indonesia` (koma pisah item, pipe pisah hz/id). Kalau null → halaman Karir di-skip otomatis. |
| 批命備註 | `dm_pos_score` / `dm_neg_score` / `wangdu_*` |
| 宿命 | `ziwei_su_ming` |
| Da Yun table / 流年易鑑 | validasi da yun cycles |

**Agent tidak perlu tahu foto ada di subfolder mana** — baca semua yang ada di `data/` dan kenali kontennya dari isi foto.

**Setelah selesai baca semua foto — sebelum tulis MD — kalau ada foto sulit dibaca:**

1. Jalankan **PowerShell tool** (bukan Bash) — substitusi nomor foto asli, JANGAN tulis literal `[NOMOR]`:
```powershell
$nums = "7, 14"   # ← ganti dengan nomor foto asli yang buram
$msg = "Foto $nums perlu retake - cek chat"
Set-Content "C:\temp\_claude_popup_tmp.vbs" "CreateObject(""WScript.Shell"").Popup ""$msg"", 8, ""Claude Retake"", 48" -Encoding ASCII
Start-Process wscript.exe -ArgumentList "C:\temp\_claude_popup_tmp.vbs"
```

2. Output template ini di chat (isi field asli):
```
⚠️ RETAKE DISARANKAN
━━━━━━━━━━━━━━━━━━━━
Foto : 7, 14
Alasan : teks terlalu kecil / buram
Field terdampak : liu_nian_2027, palace_fuqi_insight
→ Kirim foto retake di chat ini. Render tetap jalan.
━━━━━━━━━━━━━━━━━━━━
```

Kalau semua foto terbaca jelas → skip, lanjut langsung tulis MD.
Render **tidak di-stop** — tetap ekstrak semaksimal mungkin dari foto buram, tulis `null` HANYA untuk karakter/field yang benar-benar tidak terbaca.

**Format wajib di `## CATATAN retake_needed:`** (akhir MD):
```
## CATATAN retake_needed:
- foto: 7 | field: liu_nian_2027 | alasan: teks buram, angka tidak terbaca
- foto: 14 | field: palace_fuqi_insight | alasan: foto terlalu gelap
```

**Aturan wajib:**
- RULE 9 — **MARRIAGE SHIO:** Isi HANYA shio yang **TERTULIS EKSPLISIT** di foto 婚配 beserta tier-nya (大吉/次吉/忌). **DILARANG** derive, tambah, atau infer shio yang tidak disebutkan di foto. Kalau foto hanya menyebut 3 shio 大吉 → isi 3 shio saja. Jangan lengkapi sampai 12 shio.

- RULE 10 — **LIU NIAN VARIASI STRUKTUR (DIPERLUAS):**
  - Kalimat pertama tiap tahun **WAJIB berbeda** sudut pandangnya: finansial / relasi / bintang dominan / peringatan / karakter / peluang — DILARANG memulai dua tahun berbeda dengan pola yang sama.
  - **Struktur keseluruhan tiap tahun juga WAJIB berbeda** — bukan hanya kalimat pertama. Variasikan: urutan topik (karir dulu vs relasi dulu vs bintang dulu), panjang pendek paragraf, tone (peringatan vs harapan vs netral), dan cara memperkenalkan bintang.
  - **FRASA TERLARANG** (jangan muncul di lebih dari 1 tahun):
    - ❌ "usaha dan kerja keras yang [nama] curahkan sekilas tampak sebanding dengan hasil finansial"
    - ❌ "[nama] dapat memperoleh bantuan dari saudara dan teman-teman — secara nyata dapat mencapai tujuan yang cukup memuaskan. Namun dari luar, segala sesuatu tampak biasa saja"
    - ❌ "pengeluaran cukup besar dan perlu memperhatikan kondisi kesehatan tubuh"
    - ❌ "penolong sejati sulit ditemukan, dan secara nyata sulit mencapai tujuan"
  - **Cek wajib sebelum save MD:** baca semua liu_nian sekaligus — apakah ada 2 tahun yang pembukanya terasa mirip? Jika ya, rewrite salah satunya dari sudut pandang berbeda.
  - Tiap tahun harus bisa dibaca berdiri sendiri — pembaca tahu TAHUN MANA ini tanpa harus lihat angkanya.

- RULE 11 — **SINTESIS WAJIB DIISI:** Bagian `### Sintesis & Saran Aksi` di MD **WAJIB diisi** — bukan dibiarkan null. Sumber: foto 命宮 / 全局總論 / palace relevan. Isi `opening`, `trio` (kekuatan/tantangan/tindakan), dan tepat **5 items** di `actions`. Kalau halaman Sintesis kosong → Lima Langkah Praktis di PDF akan menampilkan template default yang salah.

- RULE 6: palace insight WAJIB profesional & personal. 3 syarat wajib:
  1. **Sebut nama subjek** minimal 1× (e.g. "SAID adalah sosok yang...", "Bagi SAID, ...")
  2. **Paraphrase profesional** — terjemah mengalir natural, bukan fotokopi kata per kata. Klausa count ≥80% TETAP dipertahankan, tapi dalam bahasa Indonesia yang profesional dan natural.
  3. **Setiap [[漢字]]** punya label Indonesia/pinyin sebelumnya (lihat RULE 8)

  **Contoh format BENAR** (dari foto 命宮):
  ```
  SAID adalah sosok yang tegas dan berani mengambil keputusan [[坚決果斷]] — perjalanan hidupnya bersifat aktif dan penuh gerak maju, didorong keberanian sejati untuk terus melampaui batas [[向人生不斷挑戰的勇氣]]. Di mata orang lain, SAID tampil dengan kesan lembut, terpelajar, dan elegan [[溫文儒雅]]...
  ```

  **Contoh format SALAH** (jangan seperti ini):
  ```
  Tegas dan berani. 坚決果斷 — berani menghadapi tantangan. 高尚的氣質 ...
  ```

- RULE 7: palace insight HANYA dari foto palace yang cocok persis (lihat tabel di bawah)
- RULE 8: **SETIAP `[[漢字]]` di palace insight, prose, dan kesimpulan WAJIB punya label Indonesia atau pinyin langsung sebelumnya.** Format wajib: `Label Indonesia [[漢字]]` — contoh: `Wenqu [[文曲]]`, `bintang buruk [[凶星]]`, `Bintang Sastra [[文昌星]]`. Kalau tidak tahu terjemahan → pakai pinyin transliterasi. Exception SATU-SATUNYA: ranting posisi tunggal `[[子]]`–`[[亥]]` dalam kalimat yang sudah jelas konteks posisi/istana. **Preflight akan HARD ERROR kalau ada `[[漢字]]` tanpa label Indonesia.**
- 12 palace PENUH & faithful — klausa kondisional dipertahankan — klausa count ≥80% (命宮 ≥95%)
- 5-shen wajib 5 elemen unik [金木水火土]
- Field ragu → `null` + tulis di `## CATATAN`

**RULE 7 source binding:**

| Field | Foto WAJIB | DILARANG |
|---|---|---|
| `palace_ming_gong_insight` | 【命宮】 (dari prompt) | 全局/palace lain |
| `palace_xiongdi_insight` | 【兄弟】 | 全局 |
| `palace_fuqi_insight` | 【夫妻】 | 全局/婚配 foto |
| `palace_zinu_insight` | 【子女】 | 全局/fumu |
| `palace_caibo_insight` | 【財帛】 | 全局 |
| `palace_jie_e_insight` | 【疾厄】 | 全局 |
| `palace_qianyi_insight` | 【遷移】 | 全局 |
| `palace_puyi_insight` | 【僕役】 | 全局 |
| `palace_guanlu_insight` | 【官祿】 | 事業 foto |
| `palace_tianzhai_insight` | 【田宅】 | 全局 |
| `palace_fude_insight` | 【福德】 | 全局 |
| `palace_fumu_insight` | 【父母】 | 全局 |
| `liu_nian_YYYY` | Foto tahun YYYY | foto tahun lain |

**Palace tidak ada foto → wajib:**
```
xiongdi:
- star: null
- insight: null
- action: null
```
JANGAN isi teks apapun kalau foto tidak ada. Engine auto-skip halaman tersebut.

**命宮 narrative — aturan khusus + KLAUSA-COUNT GATE (wajib diikuti):**
- **Sebelum menulis**: hitung jumlah klausa/kalimat di foto 命宮 → catat angka N
- **Setelah menulis**: hitung klausa di MD → WAJIB ≥ 0.90 × N. Kalau kurang → baca foto lagi
- Full translate faithful dari foto prompt attachment — personalisasi dengan nama subjek
- Semua kalimat diterjemahkan, tidak ada yang dipotong
- Klausa kondisional ≥95% dipertahankan (apabila/jika/bila → WAJIB diterjemah, jangan skip)
- Tulis di `## DATA` sebagai `palace_ming_gong_insight:` DAN di TAFSIR `ming_gong: insight:`
- KEDUANYA wajib sama panjang dan lengkap — preflight ERROR kalau < 700 char

**12 Palace (夫妻/子女/財帛 dst) — ANTI-RINGKAS GATE:**
- **Sebelum `photo_feeder.py next`**: verifikasi → apakah ada klausa kondisional di foto yang belum diterjemah? apakah ada paragraf yang digabung jadi 1 kalimat?
- DILARANG: merangkum 1 paragraf jadi 1 kalimat, skip klausa kondisional, gabung kalimat
- DILARANG: menulis insight < 300 char kalau foto punya konten panjang — preflight WARNING
- Personalisasi: sebut nama subjek minimal 1× tiap 3 kalimat

**Schema lengkap:** `WEB_CLAUDE_PROMPT.md` di folder ini.

---

### Step 2 — Build

```
cd C:\Users\sukam\OneDrive\Documents\Ramalan\v13
python build_pdf.py {id}
```

Lapor: path PDF, ukuran file, jumlah halaman, quality report foto.

---

### Step 3 — Rename folder

```
cd C:\Users\sukam\OneDrive\Documents\Ramalan\v13
python rename_folder_to_subject.py "{photos_dir}" {id}
```

Rename folder angka → nama subjek (e.g. `1` → `AH`). Idempoten — aman re-run.
`{photos_dir}` = path folder yang dikirim user (root folder, bukan `/data`).

---

## Retake Turn

**Trigger:** User kirim pesan dengan foto baru (retake) — tidak ada path folder, tidak ada 3 foto lengkap.

**SKIP:** PRE-FLIGHT, Step 0, Step 0.1, Step 0.5 — **jangan ulangi dari awal.**

### Protokol:

1. **Tentukan subject ID** dari konteks percakapan sebelumnya (nama/ID yang disebutkan saat render pertama, e.g. `ps`, `bz`). Kalau tidak jelas → tanya user satu kalimat: "Retake untuk subjek siapa? (ID/nama)".

2. **Baca MD subjek** yang sudah ada:
   ```
   C:\Users\sukam\OneDrive\Documents\Ramalan\v13\data\subjects\{id}.md
   ```
   Lihat `## CATATAN retake_needed:` — identifikasi field mana yang perlu diupdate.
   - Kalau `## CATATAN retake_needed:` **tidak ada** → tanya user singkat: "Field mana yang perlu diupdate dari foto retake ini?"

3. **Baca foto retake** dari prompt context (foto di-attach langsung di chat user).

4. **Patch MD** — update HANYA field yang tercantum di `retake_needed`. Jangan ubah field lain.
   - Hapus **hanya baris yang sudah dipatch** dari `## CATATAN retake_needed:` — sisakan baris yang belum dipatch.
   - Kalau tidak ada lagi baris tersisa di CATATAN → hapus seluruh section `## CATATAN retake_needed:`.
   - Kalau retake masih buram → tetap ekstrak semaksimal mungkin, null hanya yang benar-benar tidak terbaca, output template retake lagi, dan jalankan popup:
     ```powershell
     $nums = "X"   # ← nomor foto yang masih buram
     $msg = "Foto $nums masih buram - perlu retake lagi"
     Set-Content "C:\temp\_claude_popup_tmp.vbs" "CreateObject(""WScript.Shell"").Popup ""$msg"", 8, ""Claude Retake"", 48" -Encoding ASCII
     Start-Process wscript.exe -ArgumentList "C:\temp\_claude_popup_tmp.vbs"
     ```

5. **Rebuild:**
   ```
   cd C:\Users\sukam\OneDrive\Documents\Ramalan\v13
   python build_pdf.py {id}
   ```

6. Lapor field yang diupdate + path PDF baru.

---

## Checklist production (0 error)

- [ ] 3 foto (BaZi grid, 命宮, shio) di-attach di prompt
- [ ] `rename_photos_sequential.py` jalan di `data/`
- [ ] Blueprint dibaca sebelum nulis MD
- [ ] Validasi folder: foto buram ditangani
- [ ] MD ditulis inline (no subagent, no JSON intermediate)
- [ ] `photo_feeder.py init` dijalankan sebelum baca foto data/
- [ ] Tiap foto: Edit MD → `photo_feeder.py next` (structural gate)
- [ ] `build_pdf.py` PASS (preflight 0 errors)
- [ ] Post-render preflight PASS (0 BLEED/ZONE?)
- [ ] `rename_folder_to_subject.py` dijalankan — folder angka → nama subjek

---

## Summary vs V12

| | V12 | V13 |
|---|---|---|
| Agen utama | 2 (MAIN + TRANSLATOR) | **1** |
| Folder split | data/ + transelate/ wajib | **data/ saja** |
| Intermediate JSON | `tafsir_{id}.json` | **tidak ada** |
| Merge step | ada (Step 2) | **dihapus** |
| Foto salah folder | FAIL (null) | **adaptif** |
| Context rules duplikat | 2× | **1×** |
| Total pipeline steps | 7 | **5** |
| Model | Sonnet | **Sonnet** |
