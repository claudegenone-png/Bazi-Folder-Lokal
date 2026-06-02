# PROMPT REGENERATE KEIKO — paste ke chat Web Claude yang sama (foto sudah ada)

MD Keiko sebelumnya yang Anda generate punya tanggal lahir SALAH. Anda asumsikan ROC 97 (year pillar 戊子, 2008), padahal status bar foto menunjukkan ROC 98 (lunar 2009). Akibatnya seluruh interpretasi karakter, da yun, palace, dll dibangun di atas day master + year salah.

## DATA SUDAH DIVERIFIKASI ENGINE (pakai ini sebagai ground truth, JANGAN diubah)

```
nama: Keiko
hanzi: null  (atau Anda boleh transliterasi fonetis 2-3 hanzi mis. 慶子 / 惠子 jika cocok dengan nama Jepang Keiko — opsional)
gender: Wanita
lahir_tanggal: 2009-10-28   (solar Gregorian, dikonversi engine dari lunar ROC 98 / 9月11日)
lahir_jam: 11:25
pilar_tahun: 己/丑   (Year pillar = 己丑, shio = Kerbau)
pilar_bulan: 甲/戌
pilar_hari: 丙/午    (Day Master = 丙 Api Yang)
pilar_jam: 甲/午
```

## TUGAS ANDA

Regenerate **SELURUH MD Keiko dari awal** dengan DATA di atas sebagai dasar. Ikut struktur prompt awal (DATA + TAFSIR semua section + CATATAN) — bisa Anda lihat di output sebelumnya. Tapi **rebuild semua TAFSIR** karena karakter, format, da yun, palace SEMUA berubah dari interpretasi sebelumnya.

Beberapa konsekuensi penting yang harus Anda pahami:
- Day master sekarang **[[丙火]] Api Yang (Matahari)** — bukan unsur tanah. Karakter Keiko = ekspansif, hangat, terang, ekstrover (tipikal Matahari) — BUKAN gunung tenang seperti analisis sebelumnya.
- Shio Keiko = **[[丑]] Kerbau** — bukan Tikus.
- Year pilar **[[己丑]]** + month **[[甲戌]]** + day **[[丙午]]** + hour **[[甲午]]** — semua karakter dan analisis ten god harus dihitung ulang dari konfigurasi baru ini.
- Da yun arah: Wanita + tahun 己 (Yin stem) → da yun **forward** (順行). Hitung ulang 10 cycle dari pilar bulan 甲戌.
- Format BaZi: cek lagi (kemungkinan 偏印格 tidak relevan; 月 pilar 甲 ke DM 丙 = 偏印, jadi 偏印格 mungkin masih, tapi konteks beda).
- Konfigurasi Zi Wei (命主, 身主, 命宮, 身宮, 五行局, 斗君): kalau di foto ada layar Zi Wei dengan info center, baca ulang. Kalau tidak terbaca, set null untuk field-field tsb.

## ATURAN OUTPUT

- Mulai dengan `# Keiko` di baris pertama, tidak ada preamble.
- Ikut struktur prompt awal SEMUA section (DATA + TAFSIR + CATATAN).
- Konvensi `[[Hanzi]]` dipertahankan.
- Patuhi budget kata per section seperti prompt awal.
- Confidence rendah → null per sub-block.
- Sebut "Keiko" sebagai nama (bukan "Anda" terus-menerus).

Mulai regenerate sekarang.
