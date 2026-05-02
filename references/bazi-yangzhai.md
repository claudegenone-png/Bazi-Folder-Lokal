# Reference: 陽宅 Feng Shui Berbasis BaZi

**PENTING**: Sistem ini **BUKAN 八宅** (Ba Zhai 8-Mansions). Sistem ini turunan
dari **BaZi 喜用神** (Lucky Element dari chart 4 pilar). Software 星僑 V2.6
pakai sistem ini.

## Konsep Inti

| Aspek | 八宅 (8 Mansions) | **陽宅 BaZi-based (yang dipakai 星僑)** |
|-------|-------------------|----------------------------------------|
| Basis | 本命卦 dari tahun + gender | Day Master + 喜用神/忌神 dari 4 pilar |
| Output label | 生氣/天醫/延年/伏位 (4吉) + 絕命/五鬼/六煞/禍害 (4凶) | Arah favorable/unfavorable berdasarkan elemen |
| Statis/Dinamis | Statis seumur hidup | Bisa dinamis (流年方位 berubah) |
| Sumber utama | 《八宅明鏡》 | 《滴天髓》+ 《子平真詮》 |
| Penulis modern | Lin Yun, Master Chan | 邵偉華, 李居明, 陳啟銓, 鐘義明 |

## Mapping 5 Elemen → 8 Arah (後天八卦)

| Arah | 卦 | Elemen | Sub-elemen |
|------|----|----|----|
| **北** (Utara) | 坎 Kǎn | **水** | Air murni |
| **東北** (Timur Laut) | 艮 Gèn | **土** | Tanah muda/gunung |
| **東** (Timur) | 震 Zhèn | **木** | Kayu muda |
| **東南** (Tenggara) | 巽 Xùn | **木** | Kayu dewasa, juga 風 |
| **南** (Selatan) | 離 Lí | **火** | Api murni |
| **西南** (Barat Daya) | 坤 Kūn | **土** | Tanah dewasa/bumi |
| **西** (Barat) | 兌 Duì | **金** | Logam muda |
| **西北** (Barat Laut) | 乾 Qián | **金** | Logam dewasa/langit |
| **中央** | — | **土** | tidak masuk 8 arah |

## Algoritma 6-Step

```
INPUT: BaZi 4 pilar + jenis kelamin + tahun rekomendasi (流年)

STEP 1: Identifikasi 日主 (Day Master) — stem hari kelahiran
STEP 2: Analisis 旺衰 (kekuatan) → 用神 + 喜神 + 忌神
STEP 3: Map elemen → arah:
   element_to_dir = {
     木: [東, 東南],
     火: [南],
     土: [東北, 西南, 中央],
     金: [西, 西北],
     水: [北]
   }
   Y_dirs (用神 dirs) = mapping dari 用神
   K_dirs (忌神 dirs) = mapping dari 忌神

STEP 4: Hitung 流年 directions:
   太歲_dir = arah shio tahun ini
   三煞_dirs = lookup dari kelompok shio tahun
   大利方 = arah aman tahun ini

STEP 5: Assign per ruangan:
   坐山 (rumah punggung) = arah K (menekan 忌)
   向 (rumah hadap) = arah Y (mengundang 用)
   大門 (pintu) = Y ∩ 大利方
   神位 (altar) = Y (primary) + 大利方
   房間 (kamar) = Y
   床位 (kepala ranjang) = Y
   爐灶 (dapur):
     坐 = K (light)
     向 = Y (must be opposite 180°)
   坑廁 (toilet) = K (toilet "menekan" 忌神)

STEP 6: Output dengan tier label
   Tier 1 = 用神 murni
   Tier 2 = 喜神 atau 大利方
```

## Aturan Per Ruangan

### 坐山向 (Orientasi Rumah)

**Konsep**: rumah "duduk" (背) di arah 忌神, "menghadap" (向) ke arah 用神.

Pasangan valid (180°):
- 北↔南 (Utara-Selatan)
- 東↔西 (Timur-Barat)
- 東北↔西南 (Timur Laut-Barat Daya)
- 東南↔西北 (Tenggara-Barat Laut)

Contoh:
- 用神 水 → rumah 向北 (hadap utara), 坐南 (punggung selatan)
- 用神 木 → rumah 向東 atau 向東南, 坐西 atau 坐西北
- 用神 火 → rumah 向南, 坐北
- 用神 金 → rumah 向西 atau 向西北, 坐東 atau 坐東南
- 用神 土 → rumah 向東北 atau 向西南 (tidak universal, tergantung)

### 大門 (Pintu Utama)

**Aturan**: pintu dibuka di arah 用神 ATAU 大利方位 (tahun berjalan).

Output bisa multi-arah, contoh: "門路宜開北方、東方、東南方吉".

### 神位 (Altar)

**Aturan**: arah 用神 (memperkuat 氣 baik) + 大利方 (annual auspicious).

Catatan: software kadang memasukkan arah yang bukan 用神 murni (misal 南 untuk
用神 水) — kemungkinan karena tradisi geografis altar atau kombinasi 流年.

### 房間 / 床位 (Kamar dan Ranjang)

**Aturan kamar**: di sektor 用神 rumah.
**Aturan kepala ranjang**: kepala ke arah 用神, kaki ke 忌神.

Hindari kepala ranjang ke arah 忌神 atau 沖.

### 爐灶 (Dapur/Kompor)

**Prinsip "坐凶向吉"**: kompor *duduk* (背) di arah 忌神, *muka* (向) ke 用神.

Logika: api memasak "membakar" 凶 dan diarahkan ke 吉 untuk memperkuat 用神.

Contoh untuk 用神 木水, 忌神 火土:
- 爐灶 坐西北 (金, netral) 向東南 (木, 用) ✓ — perfect
- 爐灶 坐西 (金) 向東 (木) ✓ — alternatif
- 爐灶 坐北 (水, 用) 向南 (火, 忌) ✗ — terbalik

### 坑廁 (Toilet)

**Aturan**: ditempatkan di arah 忌神 untuk "menekan/membuang" energi buruk.

Contoh untuk 用神 木水, 忌神 火土:
- Toilet di 東北 (土) ✓
- Toilet di 西南 (土) ✓
- Toilet di 西 (金, netral) ✓
- Toilet di 北 (水, 用) ✗ — jangan, ini area 用神

## 流年方位 (Annual Directions)

Setiap tahun ada arah baik dan buruk yang berubah. Software memasukkan
"本年大利方位" sebagai tambahan dinamis.

### Konsep Utama

**太歲方** (Tai Sui direction)
- Arah Zodiak tahun. Tidak boleh "犯" (digali, dibangun, dihadapi langsung).
- Tahun 2026 (丙午, shio Kuda) → 太歲 di **南**
- Tahun 2018 (戊戌, shio Anjing) → 太歲 di **西北**

**歲破方** (Sui Po — kebalikan 太歲, 180°)
- 2026: 北 (kebalikan 南)
- 2018: 東南

**三煞方** (San Sha — 3 arah berbahaya)
| Tahun di kelompok | Posisi 三煞 |
|-------------------|-------------|
| 寅午戌 (Tiger/Horse/Dog years, 火局) | 北 (亥子丑) |
| 申子辰 (Monkey/Rat/Dragon, 水局) | 南 (巳午未) |
| 巳酉丑 (Snake/Rooster/Ox, 金局) | 東 (寅卯辰) |
| 亥卯未 (Pig/Rabbit/Goat, 木局) | 西 (申酉戌) |

**Tahun 2026 丙午 (Kuda)**: 寅午戌 group → 三煞 di **北**

**九宮飛星 流年** (9 Star Flying Pattern)
- 5黃廉貞 (paling buruk) — bergerak tiap tahun
- 二黑巨門 (penyakit) — bergerak tiap tahun
- Tahun 2024 甲辰: 5黃 di 中宮
- Tahun 2025 乙巳: 5黃 di 西北
- Tahun 2026 丙午: 5黃 di 西

**大利方位** = arah yang **tidak terkena** 太歲, 歲破, 三煞, 5黃, 二黑.

## Verifikasi Kasus Leana

Chart Leana: 戊戌 / 戊午 / 辛酉 / 丙申, Day Master 辛金, 用神 木水, 忌神 火土燥

Software output:
> "宅宜坐南向北大吉. 神位安東方、東南方、南方及本年大利方位吉. 門路宜開北方、東方、東南方吉. 房間宜南方、東方、東南方吉. 床位南、東南、東方吉. 爐灶宜安西北向東南方吉. 坑廁宜安於東北方、西南方、西方."

| Rekomendasi | Elemen | Sesuai 用/忌? |
|-------------|--------|--------------|
| 坐南向北 | 坐火/向水 | ✓ punggung 火-忌, hadap 水-用 |
| 神位 東 | 木 | ✓ 用 sekunder |
| 神位 東南 | 木 | ✓ 用 |
| 神位 南 | 火 | ⚠ 忌 (anomali, mungkin tradisi/大利方) |
| 神位 大利方 | dinamis | ✓ tergantung tahun |
| 門路 北 | 水 | ✓ 用 utama |
| 門路 東/東南 | 木 | ✓ 用 |
| 房間 南 | 火 | ⚠ anomali |
| 房間 東/東南 | 木 | ✓ 用 |
| 床位 南/東南/東 | 火/木/木 | mostly ✓ |
| 爐灶 坐西北 向東南 | 坐金/向木 | ✓ 坐 netral, 向 用 |
| 坑廁 東北 | 土 | ✓ 忌 |
| 坑廁 西南 | 土 | ✓ 忌 |
| 坑廁 西 | 金 | acceptable (netral) |

**Skor verifikasi: ~85% match.** Anomali utama: 南 muncul untuk 神位/房間.

**Penjelasan anomali**: software kemungkinan mengikuti tradisi geografis
sektor rumah (神位 condong ke 東/東南/南 — matahari pagi-siang) digabungkan
dengan rule 用神. Ini hybrid system.

## Edge Cases

### Day Master Sangat Lemah/Kuat (從格)

Untuk chart "ekstrem" (從強/從弱/化氣格):
- 從弱: 用神 = elemen yang mengalir mengikuti dominasi 忌神 (kontra-intuitif!)
- 從強: 用神 = elemen yang memperkuat dominasi
- 化氣格: 用神 = elemen "化" yang dihasilkan kombinasi gan

Untuk skill, kalau chart kategori 從格, lebih aman ikut isi foto langsung
(jangan re-derive arah).

### Konflik 用神 dengan 流年

Misal: 用神 水, tapi tahun ini 三煞 di 北. Solusi software:
- Sebut arah 用神 sebagai "primary" tetap baik
- Tambahkan "本年大利方位" sebagai alternatif tier-2

## Output Format untuk PDF

```markdown
## 🏛️ Bagian III: 陽宅 (Yang Zhai - Feng Shui Rumah)

> Sistem ini **BUKAN 八宅** (Eight Mansions). Sistem ini menurunkan arah
> baik/buruk dari **chart BaZi** Anda — Day Master + Lucky Element.

### Profil Anda

- **Day Master**: [Hanzi] · [Pinyin] · [Indonesia]
- **用神 (Lucky Element)**: [list]
- **忌神 (Avoid Element)**: [list]

### Arah Hadap Rumah

[transcript Hanzi asli]

**Indonesia**: Rumah ideal **menghadap [arah]** dengan punggung di **[arah]**.

Logika: [arah hadap] = elemen [Y] = 用神 Anda. Rumah "menyambut" energi baik.

### Pintu Utama (大門)

[transcript + translation]

### Altar / Tempat Suci (神位)

[transcript + translation]

Catatan: arah [Y] adalah primary. Arah [variabel] adalah "本年大利方位"
tahun [YYYY] yang kamu bisa update tiap tahun.

### Kamar Tidur & Ranjang (房間 / 床位)

[transcript + translation]

Visualisasi:
[diagram bagua dengan posisi yang direkomendasikan ditandai]

### Dapur / Kompor (爐灶)

[transcript + translation]

Penjelasan: prinsip **坐凶向吉** — kompor "duduk" di arah 忌神 (membakar
yang buruk), "menghadap" 用神 (memperkuat yang baik).

### Toilet (坑廁)

[transcript + translation]

Penjelasan: toilet di arah 忌神 = "menekan" energi yang tidak diinginkan.

### Diagram Bagua Rumah

[SVG bagua dengan 8 arah, mark hijau untuk 用神, merah untuk 忌神,
kuning untuk 大利方位]
```

## Catatan untuk Skill

1. **Input wajib**: 4 pilar lengkap + tahun untuk dihitung (流年 changes
   recommendations dinamis).
2. **Output structure**: pisahkan tier — *primer* (用神 murni), *sekunder*
   (喜/調候), *annual* (大利方 tahun X).
3. **Disclaimer**: sistem ini *bukan* 八宅. Jangan campur 生氣/天醫 labels.
4. **Edge cases**: 從格 chart butuh logic terpisah.
5. **Anomali tradisi**: software kadang masukkan arah non-用神 untuk 神位
   karena tradisi geografis (matahari pagi). Replikasi anomali ini bila
   ingin output identik dengan foto.

## Sumber

- 《滴天髓》 (徐大升 / 任鐵樵 注)
- 《子平真詮》 (沈孝瞻)
- 《八宅明鏡》 (kontras, untuk pembanding)
- 邵偉華《周易與預測學》
- 李居明 books
- 陳啟銓《八字風水實戰》
- 鐘義明《命理用神精華》(Taiwan 1995)
