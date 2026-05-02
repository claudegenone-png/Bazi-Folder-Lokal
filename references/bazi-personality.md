# Reference: Derivasi 性情 (Kepribadian) dari BaZi

Reference untuk bagian 【性情】 di output software 星僑.

## Formula Derivasi

```
[Day Master karakter dasar]
+ [十神 dominan layer]
+ [Yin/Yang modifier (急/緩, 剛/柔)]
+ [Strength balance modifier (旺/中/弱)]
= Kalimat kepribadian standar
```

## Layer 1: Karakter Dasar 10 天干 (Day Master)

| 日主 | YinYang | Imagery | Karakter (Hanzi) | Indonesia |
|------|---------|---------|-------------------|-----------|
| **甲木** | Yang | 大樹 | 正直、領導慾、固執、向上、不易彎曲、重面子 | Tegak, ambisius, keras kepala, progresif, peduli reputasi |
| **乙木** | Yin | 花草 | 柔韌、適應力、依附性、感性、外柔內剛、善交際 | Lentur, adaptif, sensitif, sosial |
| **丙火** | Yang | 太陽 | 熱情、開朗、慷慨、急躁、表現慾、無私 | Penuh semangat, ekstrover, dermawan, tidak sabar |
| **丁火** | Yin | 燈燭 | 細膩、敏感、思慮周密、外靜內熱、奉獻 | Detail, sensitif, berpikir matang, hangat di dalam |
| **戊土** | Yang | 大山 | 穩重、誠實、保守、固執、信用、行動緩 | Mantap, jujur, konservatif, terpercaya, lambat |
| **己土** | Yin | 田土 | 包容、細心、多疑、溫和、耐性、城府深 | Penerima, teliti, lembut, sabar, dalam |
| **庚金** | Yang | 刀劍 | 剛毅、果斷、義氣、剛烈、好勝 | Tegas, decisif, setia, keras, kompetitif |
| **辛金** | Yin | 珠玉 | 自尊強、敏銳、清高、堅定、外柔內剛 | Harga diri tinggi, peka, terhormat, teguh, lembut di luar tegas di dalam |
| **壬水** | Yang | 江河 | 智慧、機變、流動、包容、不拘小節、漂泊 | Cerdas, fleksibel, mengalir, toleran, tidak detail |
| **癸水** | Yin | 雨露 | 內斂、聰慧、多情、敏感、思維細膩 | Tertutup, cerdas, banyak rasa, sensitif |

## Layer 2: Modifier 十神 Dominan

| 十神 | Pinyin | Indonesia | Frase Karakter Standar |
|------|--------|-----------|------------------------|
| 比肩 | Bǐ Jiān | Sejawat | 自尊心強、固執、獨立、不服輸、行動派 |
| 劫財 | Jié Cái | Pencuri Harta | 競爭心、衝動、慷慨、社交廣 |
| 食神 | Shí Shén | Dewa Makanan | 溫和、樂觀、藝術天份、表達能力佳 |
| 傷官 | Shāng Guān | Pelukai Pejabat | 聰明、才華洋溢、傲氣、叛逆、口才好 |
| 偏財 | Piān Cái | Harta Sampingan | 慷慨、人緣好、機會多、風流、行動快 |
| 正財 | Zhèng Cái | Harta Utama | 務實、節儉、守規矩、家庭觀念重 |
| 七殺 | Qī Shā | Tujuh Pembunuh | **遇事不懼、行動較慢但富操作性、不可侵犯、自信、堅定** |
| 正官 | Zhèng Guān | Pejabat Utama | 正直、守紀律、責任感、保守、重名譽 |
| 偏印 | Piān Yìn | Cap Sampingan | 思考獨特、孤僻、敏感、靈感強、學術 |
| 正印 | Zhèng Yìn | Cap Utama | 仁慈、學識、保守、依賴、慈母性格 |

## Layer 3: Strength Modifier

| Kondisi | Efek |
|---------|------|
| 身強 + 殺旺有制 | 大將之才、有威望 (Jenderal, berwibawa) |
| 身弱 + 殺旺無制 | REFRAME → "perlu latihan asertivitas, peka terhadap energi sekitar" |
| 身強 + 食傷洩秀 | 才華橫溢、表達佳 (Berbakat, jago komunikasi) |
| 身弱 + 印重 | REFRAME → "menghargai dukungan, butuh waktu mempertimbangkan" |
| 比劫過旺 | REFRAME → "punya pendirian kuat, perlu mendengarkan" |

## Aturan Reframing Etika

| ❌ JANGAN | ✅ GANTI |
|----------|---------|
| 怯懦/膽小 | "lembut, perlu lingkungan suportif" |
| 固執自我 | "punya pendirian kuat" |
| 孤僻、人際淡薄 | "lebih nyaman dalam relasi mendalam" |
| 破財/敗運 | "tantangan finansial yang bisa diatasi" |

## Contoh Derivasi: Leana

**Chart**: 戊戌/戊午/辛酉/丙申, Day Master 辛金, 七殺 dominan

**Foto**: "遇事不懼，但不急切，富操作性，但行動較慢，不可侵犯的，但也不隨意侵犯他人，自信，堅定力強"

**Breakdown**:
1. 辛金 base = 自尊強、堅定 → "自信、堅定力強、不可侵犯"
2. 七殺 layer = 遇事不懼 → "遇事不懼"
3. 辛金 yin = refined/slow → "不急切、行動較慢"
4. 七殺 controlled → "不隨意侵犯他人"
5. 辛+殺 combo → "操作性強"

**Indonesia natural**:
> "Saat menghadapi tantangan tidak gentar, namun tidak terburu-buru. Sangat
> jago eksekusi tetapi langkahnya bertahap. Tidak mudah diintervensi, namun
> juga tidak mengganggu orang lain. Percaya diri dan teguh dalam pendirian."

## Output Format PDF

```markdown
## 性情 (Kepribadian)

> Day Master: **[Hanzi]** · [Pinyin] · [Indonesia]
> 十神 Dominan: **[Hanzi]** · [Pinyin] · [Indonesia]

### Inti Karakter
[transkrip Hanzi asli]
[translate Indonesia]

### Sisi Kekuatan
• ...

### Sisi Kompleksitas (yang bisa diolah)
• ... (reframed, no blunt negative)

### Cara Berkomunikasi
[interpretasi sosial]
```

## Glossary

| Hanzi | Pinyin | Indonesia |
|-------|--------|-----------|
| 性情 | Xìng Qíng | Kepribadian |
| 自信 | Zì Xìn | Percaya Diri |
| 堅定 | Jiān Dìng | Teguh |
| 操作性 | Cāo Zuò Xìng | Daya Eksekusi |
| 內向 | Nèi Xiàng | Introver |
| 外向 | Wài Xiàng | Ekstrover |
| 細膩 | Xì Nì | Halus / Detail |
| 急躁 | Jí Zào | Tidak Sabar |
| 善交際 | Shàn Jiāo Jì | Sosial |

## Sumber

- 《子平真詮·論十神》
- 《三命通會·論性情》卷六
- 梁湘潤《子平基礎概要》
