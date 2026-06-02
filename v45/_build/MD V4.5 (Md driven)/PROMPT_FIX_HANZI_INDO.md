# PROMPT REVISI — Indonesia primary, Hanzi opsional dalam kurung

> Paste ke chat Web Claude existing per subjek (foto + MD sudah ada).

---

Saya butuh REVISI seluruh TAFSIR di MD subjek ini. User PDF tidak bisa baca Mandarin, jadi semua istilah Hanzi harus diterjemahkan ke Indonesia di narasi.

## ATURAN BARU

Setiap kali Hanzi muncul di prosa narasi:

- **Indonesian primary, Hanzi dalam kurung opsional**
- Format: `**{Terjemahan Indonesia}** ([[Hanzi]])`
- Hanya untuk PERTAMA kali Hanzi disebut di paragraf — penyebutan berikutnya cukup Indonesia saja
- Hanzi di field DATA & label struktur (tags, mantra, motto) TIDAK perlu diubah, hanya dalam PROSA narasi

## CONTOH

❌ Sebelum:
```
[[偏印格]] memberi Keiko intuisi kreatif tajam. Aktifkan [[木]] dan [[水]] lewat seni. Fase [[丙子]] membawa momentum.
```

✅ Sesudah:
```
**Format Mentor Bayangan** ([[偏印格]]) memberi Keiko intuisi kreatif tajam. Aktifkan unsur **Kayu** ([[木]]) dan **Air** ([[水]]) lewat seni. Fase **Api Yang Tikus** ([[丙子]]) membawa momentum.
```

## DAFTAR TERJEMAHAN STANDAR (gunakan ini)

**10 Stems (Hari/Bulan/Tahun/Jam):**
- 甲 = Kayu Yang | 乙 = Kayu Yin | 丙 = Api Yang | 丁 = Api Yin | 戊 = Tanah Yang
- 己 = Tanah Yin | 庚 = Logam Yang | 辛 = Logam Yin | 壬 = Air Yang | 癸 = Air Yin

**12 Branches (cabang):**
- 子 = Tikus | 丑 = Kerbau | 寅 = Macan | 卯 = Kelinci | 辰 = Naga | 巳 = Ular
- 午 = Kuda | 未 = Kambing | 申 = Monyet | 酉 = Ayam | 戌 = Anjing | 亥 = Babi

**5 Elemen:**
- 金 = Logam | 水 = Air | 木 = Kayu | 火 = Api | 土 = Tanah

**10 Ten God (十神):**
- 比肩 = Pundak Sama | 劫財 = Saudara Sebanding | 食神 = Pencipta Lembut | 傷官 = Kritikus Tajam
- 偏財 = Rezeki Tak Terduga | 正財 = Rezeki Tetap | 七殺 = Pemurnian | 正官 = Penjaga Disiplin
- 偏印 = Mentor Bayangan | 正印 = Pelajar Tekun

**Format BaZi (格局):**
- 偏印格 = Format Mentor Bayangan | 正印格 = Format Pelajar Tekun
- 七殺格 = Format Pemurnian | 正官格 = Format Penjaga Disiplin
- 偏財格 = Format Rezeki Tak Terduga | 正財格 = Format Rezeki Tetap
- 食神格 = Format Pencipta Lembut | 傷官格 = Format Kritikus Tajam
- 比肩格 = Format Pundak Sama | 劫財格 = Format Saudara Sebanding

**14 Star Zi Wei:**
- 紫微 = Pemimpin Agung | 天機 = Strategi | 太陽 = Matahari | 武曲 = Disiplin Material
- 天同 = Harmoni | 廉貞 = Integritas | 天府 = Lumbung | 太陰 = Bulan/Intuisi
- 貪狼 = Hasrat | 巨門 = Pintu Besar | 天相 = Penolong | 天梁 = Pelindung
- 七殺 = Pemurnian | 破軍 = Pembongkar

**Shen Sha umum:**
- 驛馬 = Bintang Perpindahan | 桃花 = Bintang Daya Pikat | 文昌 = Bintang Akademik
- 華蓋 = Bintang Naungan Spiritual | 天乙 / 天乙貴人 = Bintang Penolong | 紅鸞 = Bintang Asmara

**Pilar gabungan (mis. 丙子, 戊午, dll):** sebut sebagai "{Stem-trans} {Branch-trans}" atau "Pilar [[Hanzi]] ({Stem-trans + Branch-trans})". Contoh: 丙子 = "Api Yang Tikus" atau "Pilar Api Yang Tikus".

**Trigram (8 卦):**
- 乾 = Langit | 坤 = Bumi | 震 = Petir | 巽 = Angin
- 坎 = Air | 離 = Api | 艮 = Gunung | 兌 = Danau

## TUGAS ANDA

Regenerate **HANYA bagian `## TAFSIR`** dari MD subjek ini dengan konvensi baru di atas. Ikut struktur identik dengan output sebelumnya (semua 14 sub-section tetap ada, semua sub-fields tetap ada). 

JANGAN ubah:
- Section `## DATA`
- Section `## CATATAN`
- Field-field struktur seperti `radar_traits`, `motto`, `mantra` (Hanzi di sini boleh tetap karena bukan narasi)
- Hanzi di tags, fic-vibe, atau label kartu (bukan narasi)

YANG diubah:
- Semua paragraf narasi (`paragraf:`, `body:`, `insight:`, `headline:`, `intro:`, `quote:`, `opening:`, `lalu/sekarang/berikutnya:`, dan deskripsi lain)

## ATURAN OUTPUT

- Mulai dengan `## TAFSIR` di baris pertama
- Selesai sebelum `## CATATAN`
- Tidak ada teks pengantar
- Patuhi konvensi Indonesian primary, Hanzi dalam kurung
- DILARANG pakai em-dash (—) atau en-dash (–), gunakan koma (,)
- Sebut nama subjek di sekitar 30% kalimat

Mulai output sekarang.
