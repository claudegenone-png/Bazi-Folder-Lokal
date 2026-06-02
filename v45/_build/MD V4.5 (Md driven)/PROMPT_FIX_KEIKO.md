# PROMPT FIX KEIKO — paste ke chat Web Claude yang sama (foto Keiko sudah ada)

Ada koreksi tanggal lahir Keiko di MD yang Anda generate. Anda tulis `lahir_tanggal: 2008-11-09` sebagai estimasi konversi lunar→solar — itu salah. Native compute mengkonfirmasi pilar tidak match (engine compute month `癸亥`, MD-nya `壬戌`).

Solar yang benar untuk Keiko ≈ **2008-10-09** atau **2008-10-10** (perlu konfirmasi tepat dari Anda).

## Tugas Anda

Cek ulang foto Keiko, lalu jawab dalam format ini SAJA (tidak ada teks lain):

```
LUNAR_ROC_YEAR: {ROC year tertulis di foto, mis. 97 atau 98 — angka EXACT yang muncul}
LUNAR_YEAR_PILLAR: {2 hanzi year pillar, mis. 戊子}
LUNAR_MONTH: {bulan lunar, angka 1-12 atau "閏N" kalau lunar leap month}
LUNAR_DAY: {hari lunar, angka 1-30}
JAM_LAHIR: {HH:MM 24-jam, mis. 11:25}
SOURCE_PHOTO: {Image # batch # mana yang Anda baca info ini, mis. "Image 4 batch 1"}

CROSS_CHECK_PILLARS:
- year: {2 hanzi yang TERLIHAT di foto pillar grid}
- month: {2 hanzi}
- day: {2 hanzi atau "TIDAK TERBACA"}
- hour: {2 hanzi atau "TIDAK TERBACA"}

NOTE_CONFIDENCE: {1 kalimat — apakah Anda yakin atau ragu, dan kenapa}
```

## ATURAN KETAT

- **JANGAN** konversi lunar → solar sendiri. Saya akan handle konversi pakai engine sxtwl.
- **JANGAN** tebak. Kalau angka tidak terbaca jelas → tulis "TIDAK TERBACA".
- **WAJIB** konsisten: kalau LUNAR_YEAR_PILLAR = 戊子, maka tahun lunar 2008 (siklik) — tidak boleh ROC 98 (2009) jika year pillar 戊子. ROC 97 = 2008 lunar = year pilar 戊子.
- Kalau Anda tidak yakin antara ROC 97 vs ROC 98 → tulis ROC year EXACT yang Anda lihat di foto (jangan koreksi).
- Hanya format di atas, no preamble, no closing.

Mulai jawab.
