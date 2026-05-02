---
name: xingqiao-fortune-id
description: |
  Skill kustom untuk mengkonversi foto-foto hasil ramalan dari software Taiwan
  "四柱論命附加紫微斗數 V2.6" (星僑 / NCC) menjadi laporan PDF berbahasa Indonesia
  yang detail (~23 halaman) dengan layout klasik Tionghoa (merah-emas, ornamen,
  kaligrafi). Skill ini menggabungkan BaZi 八字四柱 + Zi Wei Dou Shu 紫微斗數 +
  Yang Zhai 陽宅 (feng shui berbasis BaZi, BUKAN 八宅) + 神煞 + 婚配 + 事業.

  V2 ARCHITECTURE: deterministik. Skill pakai Python orchestrator
  (lib/bazi_calc.py + lib/shio_compat.py + lib/render.py) untuk membangun
  HTML self-contained dari frozen design system (template/style.css).
  Claude HANYA bertugas: (1) OCR foto → transcript bilingual, (2) panggil
  Python untuk render, (3) jalankan Chrome headless untuk PDF. Tidak ada
  HTML/CSS yang digenerate ad-hoc oleh LLM.

  Dirancang untuk SETIA terhadap isi foto: skill membaca teks Hanzi di foto,
  menerjemahkan ke Indonesia, dan menyusun ulang menjadi laporan cantik.
  Skill TIDAK menghasilkan ramalan baru di luar yang ada di foto.

  TRIGGER PHRASES (Indonesian): "bikin laporan ramalan", "buat laporan ramalan",
  "convert foto ramalan ke PDF", "laporan ramalan dari foto", "ramalan china pdf",
  "bikin pdf ramalan", "ramalan dari folder", "ramalan dari foto Mike/Leana/dll",
  "bazi pdf indonesia", "laporan ziwei indonesia", "ramalan taiwan pdf".
  TRIGGER FILES: folder berisi foto JPEG/PNG dengan header 星僑 + 四柱論命附加紫微斗數 V2.6.

  COORDINATES WITH:
  - Bash + Python (untuk jalanin lib/render.py)
  - Bash + Chrome headless (untuk konversi HTML → PDF final)
  - Claude vision (untuk OCR foto Hanzi → text bilingual)
  - frontend-design (OPSIONAL) — hanya kalau user minta polish design
    di luar frozen system, atau kalau ada bug visual yang harus di-debug.

  TIDAK berlaku untuk: input data lahir murni tanpa foto (gunakan bazi-fortune /
  ziwei-fortune), foto sumber non-星僑, ramalan sistem lain (tarot/numerology/dll).
license: MIT
metadata:
  author: kingston-sukamto
  version: "2.0.0"
  language: id
  tags: ["xingqiao", "bazi", "ziwei", "fengshui", "pdf", "indonesia", "fortune"]
---

# Skill: Ramalan 星僑 → Laporan PDF Indonesia (V2)

Mengkonversi foto-foto output software ramalan Taiwan `四柱論命附加紫微斗數 V2.6`
menjadi laporan PDF berbahasa Indonesia (~23 halaman) dengan layout klasik
Tionghoa.

## Konteks Software

Software sumber: **NCC / 星僑五術** (ncc.com.tw), Taiwan, sejak 1990an.
Author: 陳恩國 (konten), 陳慶鴻 (programmer). 台內著字第72685號.

Methodology software (multi-school):
- **三命通會** (Wan Yumin) — sumber utama 230 神煞
- **子平真詮** (Shen Xiaozhan) — kerangka 格局 + 十神
- **滴天髓** (atribusi Liu Bowen) — analisis 旺衰 day master
- **窮通寶鑑** — pemilihan 喜用神 berbasis musim

## Arsitektur V2 — Mengapa Deterministik

Iterasi V1 mengandalkan LLM untuk generate HTML/CSS dari scratch via
frontend-design skill. Hasilnya: layout drift antar run, overflow margin,
dan inkonsistensi visual.

V2 memindahkan rendering ke Python:

```
foto folder ─┬─► OCR (Claude vision) ──► transcripts dict
             │
             └─► subject info (nama, lahir, gender) ──┐
                                                      ▼
                              bazi_calc.full_chart(...) ──► chart dict
                                                      │
                                                      ▼
                              render.render_to_file(data) ──► report.html
                                                      │
                                                      ▼
                                          Chrome headless ──► report.pdf
```

Komponen Python:

| File | Tugas |
|------|------|
| [lib/bazi_calc.py](lib/bazi_calc.py) | Calculator 4 pilar, Day Master, 5 elemen, 大運 cycles, 格局, 喜/忌神 |
| [lib/shio_compat.py](lib/shio_compat.py) | Tabel 12×12 kompatibilitas shio (三合/六合/六沖/六害/三刑) |
| [lib/render.py](lib/render.py) | Orchestrator HTML — generate radar Wu Xing, compatibility wheel, 大運 timeline, dan susun 23 halaman dari template |
| [template/style.css](template/style.css) | Frozen design system (anti-overflow) |
| [SVG Shio/V2/](SVG%20Shio/V2/) | 24 file SVG shio (12 hewan × 2 warna) |

LLM tidak menulis HTML/CSS apa pun. Dia hanya mengisi data structure.

## Quick Start

```
"Bikin laporan ramalan dari folder C:\Users\josuk\Downloads\Ramalan Leana"
   ↓
Step 1: scan foto, OCR semua kategori
Step 2: bangun input dict (subject + chart + transcripts)
Step 3: python lib/render.py input.json -o cache/report.html
Step 4: Chrome headless --print-to-pdf → Ramalan_Leana.pdf
   ↓
Output: Ramalan_Leana.pdf (~23 halaman, ~800KB)
```

## Workflow Detil

### Step 1 — Scan Folder Foto

Glob `*.jpeg` / `*.jpg` / `*.png` di folder yang user berikan. Setiap foto
adalah screenshot software 星僑. Header `【XXX】` di tengah layar
mengidentifikasi kategori.

Lihat [references/software-format.md](references/software-format.md) untuk
17 kategori standar dan cara mengenalinya.

### Step 2 — Identifikasi Subjek

Cari foto chart utama (tabel 4 kolom besar). Ekstrak via Claude vision:

- **Nama subjek** (bottom: `姓名: NAMA [男/女]`)
- **Gender**: 男 (M) / 女 (F)
- **Tanggal lahir**: 國曆 (西元) + 農曆 — konversi 民國 + 1911 = 西元
- **Jam lahir**: HH:MM (untuk hour pillar)

Tidak perlu lagi mencatat 4 pilar / 喜用神 / 大運 dari foto, karena
**bazi_calc.py akan menghitung ulang dari tanggal lahir**.

Itulah keuntungan V2: data chart deterministik, foto hanya untuk transcript.

### Step 3 — Klasifikasi & OCR Setiap Foto

Untuk tiap foto teks, identifikasi kategori berdasarkan header `【XXX】`:

**Kategori BaZi (7):** 性情, 全局總論, 神煞, 財富, 婚配, 事業, 陽宅

**Kategori Zi Wei (12):** 命宮, 兄弟, 夫妻, 子女, 財帛, 疾厄, 遷移, 僕役,
官祿, 田宅, 福德, 父母

Untuk setiap foto teks:
1. **Transkrip Hanzi verbatim** (pertahankan `◎ • ⚪` markers). Tag bagian blur dengan `[?tidak terbaca]`.
2. **Translate ke Indonesia** memakai glossary di [references/](references/).
3. **Tulis Tafsir / Saran Praktis fresh** — 3-5 bullet point Indonesia, personal &
   nyambung dengan transkrip + chart subjek (Day Master, format, 喜用神, shio,
   fase 大運 sekarang). Ini WAJIB di-generate per orang, bukan template generik.

**Mengapa tafsir harus fresh per orang (option A)**:
- Transkrip software adalah teks template generic; nilai tambah laporan ada di
  *cara membaca* transkrip itu untuk subjek spesifik ini.
- Tafsir harus mengaitkan: isi transkrip ↔ Day Master ↔ shio ↔ format ↔ fase
  大運 sekarang ↔ situasi gender/umur. Itu tidak bisa di-template.
- Trade-off: ~5-10rb token tambahan per laporan. Diterima sebagai biaya layanan.

**Aturan tafsir** (etika WAJIB):
- Pakai bahasa pemberdayaan: "kecenderungan", "potensi", "trend".
- Reframing konstruktif untuk hal negatif: "tantangan ini bisa diatasi dengan ..."
- TIDAK BOLEH menambah prediksi yang tidak ada dasar di transkrip + chart.
- Maksimal 3-5 bullet, masing-masing 1-2 kalimat singkat.

Hasilkan struktur `transcripts`:

```python
transcripts = {
  "性情": {
    "hanzi": "...",            # WAJIB — transkrip foto
    "indonesia": "...",        # WAJIB — terjemahan
    "tafsir": [                # WAJIB — 3-5 bullet point Indonesia, fresh per orang
      "Bullet 1 — kaitkan dengan Day Master 庚金 yang kuat...",
      "Bullet 2 — di fase 大運 丙辰 sekarang, kecenderungan ...",
      "Bullet 3 — saran praktis: ...",
    ],
  },
  # ... dst untuk semua kategori yang ada di folder
}
```

Kategori yang fotonya tidak ada → skip dari dict; render.py otomatis tampilkan
note "foto tidak tersedia".

### Step 4 — Translate dengan Konsistensi

Glossary references:
- [shensha-catalog.md](references/shensha-catalog.md) — terjemahan 32 神煞
- [ziwei-12palaces.md](references/ziwei-12palaces.md) — istilah Zi Wei
- [bazi-personality.md](references/bazi-personality.md) — istilah karakter
- [bazi-relationships.md](references/bazi-relationships.md) — istilah keluarga
- [bazi-marriage-shio.md](references/bazi-marriage-shio.md) — istilah shio
- [bazi-career-industries.md](references/bazi-career-industries.md) — istilah karir
- [bazi-yangzhai.md](references/bazi-yangzhai.md) — istilah feng shui

**Aturan translate:**
- **Pertahankan Hanzi penting** dalam tanda kurung: `Bintang Bunga Persik (桃花)`
- **Istilah teknis 4 lapis**: Indonesia + Hanzi + Pinyin + arti
  - `Day Master 辛金 (Xin Jin / Logam Yin) — Anda berelemen Logam Halus`
- **Idiom diterjemahkan padanan, bukan literal**:
  - 逢凶化吉 → "ancaman berubah jadi keberuntungan"
- **Etika reframing**: lihat bagian "Reframing Negatif" di bazi-personality.md

### Step 5 — Bangun Input Dict & Panggil Renderer

Tulis file JSON sementara di `cache/_input_{NamaSubjek}.json`:

```json
{
  "subject": {
    "name": "Leana",
    "gender": "F",
    "birth_solar": "1985-08-15 14:30",
    "birth_lunar": "民國 74 年 7 月 1 日"
  },
  "chart": <hasil bazi_calc.full_chart(1985, 8, 15, 14, "F")>,
  "transcripts": { ... },
  "current_age": 39
}
```

Cara cepat: panggil bazi_calc dari skrip kecil:

```bash
python -c "
import sys, json
sys.path.insert(0, 'lib')
from bazi_calc import full_chart
chart = full_chart(1985, 8, 15, 14, 'F')
json.dump(chart, open('cache/_chart_leana.json','w',encoding='utf-8'),
          ensure_ascii=False, indent=2)
"
```

Lalu render:

```bash
python lib/render.py cache/_input_leana.json -o cache/report.html
```

### Step 6 — Convert HTML → PDF (Chrome headless)

```bash
"C:/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless --disable-gpu \
  --print-to-pdf="C:/Users/josuk/Downloads/Ramalan_Leana.pdf" \
  --no-pdf-header-footer \
  "file:///C:/Users/josuk/OneDrive/Documents/Ramalan/cache/report.html"
```

Verify:
- File PDF terbentuk dengan ukuran > 500 KB
- Buka PDF, scroll cepat untuk pastikan layout tidak rusak
- Cek tidak ada element ke-crop di tepi halaman
- Cek footer hanya nomor halaman (tanpa Hanzi 福/壽/財)
- Cek 4 chart visual masuk: 4-pilar, Wu Xing radar, compatibility wheel, 大運 bar

Output filename: `Ramalan_{NamaSubjek}_{YYYYMMDD}.pdf`

## Struktur Output PDF (~23 halaman)

```
HALAMAN  1  | Cover (radial gradient merah-emas, SVG shio besar)
HALAMAN  2  | Daftar Isi
HALAMAN  3  | Pengantar & Disclaimer
HALAMAN  4  | Profil Subjek + Day Master + Chart 4 Pilar + 喜/忌神

═══ BAGIAN I — BAZI 八字四柱 ═══
HALAMAN  5  | Section opener
HALAMAN  6  | Day Master & Wu Xing radar + bar
HALAMAN  7  | 性情 (Kepribadian) — transkrip
HALAMAN  8  | 全局總論 — transkrip
HALAMAN  9  | 神煞 — transkrip
HALAMAN 10  | 財富 — transkrip
HALAMAN 11  | 婚配 + Compatibility Wheel + Grid SVG shio cocok/hindari
HALAMAN 12  | 事業 + grid 5 elemen → industri
HALAMAN 13  | 陽宅 — transkrip
HALAMAN 14  | 大運 timeline bar chart + detail per fase

═══ BAGIAN II — ZI WEI 紫微斗數 ═══
HALAMAN 15  | Section opener
HALAMAN 16  | Overview 12 palace (snippet)
HALAMAN 17  | 命宮 + 兄弟 + 夫妻 + 子女
HALAMAN 18  | 財帛 + 疾厄 + 遷移 + 僕役
HALAMAN 19  | 官祿 + 田宅 + 福德 + 父母

═══ BAGIAN III — PENUTUP ═══
HALAMAN 20  | Section opener
HALAMAN 21  | Sintesis & Saran Action
HALAMAN 22  | Glossary Istilah Tionghoa
HALAMAN 23  | Disclaimer & Etika
```

## Etika Penyajian (Wajib)

❌ **DILARANG**:
- Prediksi kematian dalam bentuk apapun
- Kalimat absolut ("PASTI akan ...", "TIDAK MUNGKIN ...")
- Bahasa menakutkan/intimidasi
- Diagnosa medis/hukum spesifik
- Promosi jasa "ubah nasib" berbayar

✅ **WAJIB**:
- Bahasa pemberdayaan: "kecenderungan", "trend", "potensi", "bisa jadi"
- Negative framing dibalik konstruktif: "tantangan ini bisa diatasi dengan ..."
- Saran berbasis data dari foto, bukan opini bebas
- Disclaimer di setiap PDF (sudah otomatis di halaman terakhir)

## Cek Konsistensi Data

Sebelum render, cross-check:
1. **Tahun lahir 民國 + 1911 = tahun 西元** — verifikasi konversi
2. **Day Master hasil bazi_calc cocok dengan 喜用神 di foto** — kalau tidak match,
   pertanyakan jam lahir (sering off karena solar term boundary)
3. **Shio di pojok kanan foto cocok dengan year_pillar.branch dari bazi_calc**
4. **Jumlah palace Zi Wei = 12** — kalau kurang, foto belum lengkap
5. **Bagian wajib 7 BaZi + 12 Zi Wei = 19 kategori** — kalau kurang, kasih tau
   user kategori apa yang missing

## Error Handling

| Skenario | Tindakan |
|----------|---------|
| Folder tidak ditemukan | Tanya path yang benar |
| Folder kosong / no JPEG | "Folder kosong. Pastikan foto di folder ini." |
| Foto blur tidak terbaca | Lanjut dengan tag `[?]`, lapor di akhir |
| Tanggal lahir tidak terbaca | Tanya user manual |
| Foto bukan dari 星僑 | "Foto sepertinya bukan output software 星僑 V2.6. Konfirmasi?" |
| Chrome tidak ada | Pakai Edge: `"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"` |
| Bagian 陽宅 missing | Tetap render, halaman ini tampil note "tidak tersedia" |
| Bagian Zi Wei missing | Tetap render, halaman 12-palace tampil note |

## Tools yang Dibutuhkan

- **Read** — baca foto satu-satu (Claude vision)
- **Write** — generate JSON input + simpan output
- **Bash** — jalankan Python + Chrome headless
- **Glob** — scan folder foto

Tidak perlu OCR external — Claude vision langsung. Tidak perlu library Python
external — `bazi_calc`, `shio_compat`, `render` semua pure stdlib.

## Test & Demo

Quick demo render tanpa foto (pakai data Henry yang sudah cached):

```bash
cd "C:/Users/josuk/OneDrive/Documents/Ramalan"
python lib/render.py
# → cache/report.html (118 KB, 23 halaman)
```

Kemudian convert ke PDF dengan command Chrome di atas. Hasil di
`cache/report_test_henry.pdf` (~826 KB).

## References

Folder [references/](references/):

- `software-format.md` — Struktur output software 星僑 (17 kategori)
- `shensha-catalog.md` — 32 神煞 dengan rumus + interpretasi
- `ziwei-12palaces.md` — 12 palace + 14 bintang + 廟旺陷 + 四化
- `bazi-yangzhai.md` — Feng shui dari BaZi (BUKAN 八宅)
- `bazi-personality.md` — Derivasi 性情 (Day Master × 十神) + Reframing Negatif
- `bazi-relationships.md` — 全局總論 keluarga (template kalimat)
- `bazi-marriage-shio.md` — Kompatibilitas 12 shio (3合/6合/6沖/6害/3刑)
- `bazi-career-industries.md` — 5 elemen → industri Taiwan 1990s
- `pdf-template.md` — Skeleton HTML/CSS reference (sekarang di-encode di lib/render.py)

## Disclaimer

Laporan yang dihasilkan skill ini **murni untuk referensi tradisi & eksplorasi
diri**. Ramalan Tionghoa (BaZi, Zi Wei Dou Shu, Yang Zhai) adalah bagian dari
budaya Tionghoa klasik, **bukan ilmu pasti** dan **tidak menggantikan**
keputusan medis, hukum, atau finansial profesional.

Skill ini mengkonversi data foto secara setia, tetapi:
- Tidak memverifikasi kebenaran ramalan asli
- Tidak menambah prediksi di luar foto
- Tidak menjamin akurasi terjemahan untuk istilah klasik (lihat glossary)
