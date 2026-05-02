# Catatan Keputusan — Skill Ramalan v2

Dokumen ini berisi keputusan arsitektur yang diambil user untuk skill ramalan.
**Wajib dibaca di awal session baru sebelum build / refactor.**

## Tafsir / Saran Praktis per Halaman

**Keputusan: OPSI A — Tafsir fresh dari LLM untuk setiap orang.**

- ❌ Opsi B (template tafsir statis per day master): di-skip
- ❌ Opsi C (hybrid LLM transkrip + tafsir statis): sudah dicoba, **hasilnya jelek**
- ✅ **Opsi A (semua tafsir di-generate fresh oleh LLM per orang)**: dipilih

**Implikasi untuk workflow & kode:**
- Tidak perlu folder `template/tafsir/` (hapus dari plan)
- Tidak perlu file JSON template tafsir per day master (geng_jin.json, dll.)
- LLM yang tulis tafsir personal nyambung dengan transkrip Hanzi tiap halaman
- Token cost per orang naik ~5-10rb tokens — diterima karena kualitas lebih penting
- Tafsir tetap di-cache dalam `cache/<Nama>/data.json` setelah generated → re-render orang yang sama tetap instant tanpa LLM

**Alasan user:** "tafsir BaZi/Zi Wei berulang antar orang" ternyata tidak true dalam praktek — tafsir generic terasa flat dan tidak nyambung dengan transkrip spesifik. Personal lebih bernilai.

## Konsekuensi untuk struktur file

```
OneDrive/Documents/Ramalan/
├── lib/
│   ├── bazi_calc.py        ✅ ada (tested)
│   ├── shio_compat.py      ✅ ada
│   └── render.py           ⏳ belum dibangun
├── template/
│   ├── style.css           ✅ ada (frozen)
│   └── tafsir/             ❌ TIDAK PERLU (sesuai keputusan ini)
├── cache/
│   └── <Nama>/data.json    ⏳ generated per orang, simpan tafsir di sini
├── references/             ✅ ada
└── SVG Shio/V2/            ✅ ada
```

## Workflow yang berlaku

1. AI scan folder + filter target name
2. AI extract birth data dari foto chart utama
3. **Python `bazi_calc.py`** → calculated data (pilar, Wu Xing, Da Yun, dll) [no LLM]
4. **Python `shio_compat.py`** → kompatibilitas shio [no LLM]
5. AI batch-process tiap foto kategori:
   - Klasifikasi kategori (`【XXX】`)
   - Transkrip Hanzi
   - Translate ke Indonesia
   - **Tulis tafsir/saran praktis 3-5 bullet** ← bagian ini dari LLM, bukan template
6. **Python `render.py`** → assemble HTML + Chrome headless → PDF

## Estimasi token (revisi setelah opsi A)

| Skenario | Sebelumnya (opsi C) | Sekarang (opsi A) |
|----------|---------------------|-------------------|
| Generate orang baru | ~25-35K tokens | **~35-50K tokens** |
| Re-generate orang yang sama (cache) | 0 tokens | **0 tokens** (cache tetap) |

Penghematan vs Henry awal (~150K tokens) tetap **~65-77%**.
