# Reference: 婚配 — Kompatibilitas Shio (12 Zodiak Tionghoa)

Reference untuk bagian 【婚配】 di output software 星僑.
**100% deterministic** dari aturan 三合/六合/六沖/六害/三刑.

## Rules Komplet

### 三合 (Three Harmony) — Paling Positif

| Trinitas | Animals (Indonesia) | Element |
|----------|---------------------|---------|
| 申子辰 | Monyet, Tikus, Naga | 水 |
| 巳酉丑 | Ular, Ayam, Kerbau | 金 |
| 寅午戌 | Macan, Kuda, Anjing | 火 |
| 亥卯未 | Babi, Kelinci, Kambing | 木 |

### 六合 (Six Harmony) — Sekunder Positif

| Pair | Animals |
|------|---------|
| 子丑 | Tikus + Kerbau |
| 寅亥 | Macan + Babi |
| 卯戌 | Kelinci + Anjing |
| 辰酉 | Naga + Ayam |
| 巳申 | Ular + Monyet |
| 午未 | Kuda + Kambing |

### 六沖 (Six Conflicts) — Negatif Kuat

| Pair | Animals |
|------|---------|
| 子午 | Tikus ↔ Kuda |
| 丑未 | Kerbau ↔ Kambing |
| 寅申 | Macan ↔ Monyet |
| 卯酉 | Kelinci ↔ Ayam |
| 辰戌 | Naga ↔ Anjing |
| 巳亥 | Ular ↔ Babi |

### 六害 (Six Harms) — Sekunder Negatif

| Pair | Animals |
|------|---------|
| 子未 | Tikus ↔ Kambing |
| 丑午 | Kerbau ↔ Kuda |
| 寅巳 | Macan ↔ Ular |
| 卯辰 | Kelinci ↔ Naga |
| 申亥 | Monyet ↔ Babi |
| 酉戌 | Ayam ↔ Anjing |

### 三刑 (Three Punishments) — Negatif

| Type | Members |
|------|---------|
| 無恩之刑 | 寅巳申 (Macan, Ular, Monyet) |
| 持勢之刑 | 丑戌未 (Kerbau, Anjing, Kambing) |
| 無禮之刑 | 子卯 (Tikus, Kelinci) |
| 自刑 | 辰辰, 午午, 酉酉, 亥亥 |

## Tabel Kompatibilitas Per Shio

| 生肖 | Indonesia | 三合 (大吉) | 六合 (次吉) | 六沖 (忌) | 六害 (忌) | 三刑 (忌) |
|------|-----------|-------------|-------------|-----------|-----------|-----------|
| 鼠 子 | Tikus | Monyet, Naga | Kerbau | Kuda | Kambing | Kelinci |
| 牛 丑 | Kerbau | Ular, Ayam | Tikus | Kambing | Kuda | Anjing, Kambing |
| 虎 寅 | Macan | Kuda, Anjing | Babi | Monyet | Ular | Ular, Monyet |
| 兔 卯 | Kelinci | Babi, Kambing | Anjing | Ayam | Naga | Tikus |
| 龍 辰 | Naga | Monyet, Tikus | Ayam | Anjing | Kelinci | Naga |
| 蛇 巳 | Ular | Ayam, Kerbau | Monyet | Babi | Macan | Macan, Monyet |
| 馬 午 | Kuda | Macan, Anjing | Kambing | Tikus | Kerbau | Kuda |
| 羊 未 | Kambing | Babi, Kelinci | Kuda | Kerbau | Tikus | Kerbau, Anjing |
| 猴 申 | Monyet | Tikus, Naga | Ular | Macan | Babi | Macan, Ular |
| 雞 酉 | Ayam | Ular, Kerbau | Naga | Kelinci | Anjing | Ayam |
| **狗 戌** | **Anjing** | **Macan, Kuda** | **Kelinci** | **Naga** | **Ayam** | **Kerbau, Kambing** |
| 豬 亥 | Babi | Kelinci, Kambing | Macan | Ular | Monyet | Babi |

## Verifikasi Leana (生肖 狗)

Foto: "忌：配相牛、龍、羊、雞... 宜：配相虎、兔、馬大吉，其他生相次吉"

| Software | Aturan | ✓ |
|----------|--------|---|
| 宜配虎 | 三合 寅午戌 | ✓ |
| 宜配馬 | 三合 寅午戌 | ✓ |
| 宜配兔 | 六合 卯戌 | ✓ |
| 忌配龍 | 六沖 辰戌 | ✓ |
| 忌配雞 | 六害 酉戌 | ✓ |
| 忌配牛 | 三刑 丑戌未 | ✓ |
| 忌配羊 | 三刑 丑戌未 | ✓ |

**100% match.**

Aturan output software:
- **大吉** = 三合
- **次吉** = 六合
- **其他次吉** = neutral (5 sisa shio yang tidak masuk 沖/害/刑)
- **忌** = 六沖 + 六害 + 三刑 (gabungan)

## Standard Sentence Templates

| Kombinasi | Frase |
|-----------|-------|
| 三合 | 大吉、夫妻和睦、互助、白頭偕老 |
| 六合 | 次吉、感情融洽、互補 |
| 六沖 | 大忌、口角不斷、聚少離多 |
| 六害 | 暗中傷害、貌合神離 |
| 三刑 | 刑剋、爭執、感情破裂 |
| 自刑 | 自尋煩惱、性格相似但內耗 |

## Output Format PDF

```markdown
## 婚配 (Kompatibilitas Pernikahan)

> Shio Anda: **[Nama Hanzi]** · [Indonesia] · [Element]

### Pasangan Sangat Cocok (大吉 - 三合)
[Daftar shio dengan emoji + alasan]
• 🐯 **Macan (寅)** — Trinitas Api 寅午戌
• 🐴 **Kuda (午)** — Trinitas Api 寅午戌

Logika: Anda + dua shio ini membentuk **三合** (Three Harmony) — energi yang
saling mendukung dan harmonis.

### Pasangan Cocok (次吉 - 六合)
• 🐰 **Kelinci (卯)** — 六合 dengan 戌

### Pasangan Netral (其他次吉)
[Daftar 5 shio sisa dengan komentar singkat]

### Pasangan Perlu Dihindari (忌)
• 🐉 **Naga (辰)** — 六沖 dengan 戌
• 🐔 **Ayam (酉)** — 六害 dengan 戌
• 🐂 **Kerbau (丑)** — 三刑 dengan 戌
• 🐐 **Kambing (未)** — 三刑 dengan 戌

[REFRAME: bukan berarti pasti gagal — perlu effort lebih untuk merawat
hubungan, atau perlu komunikasi terbuka untuk overcome perbedaan natural]
```

## Aturan Reframing untuk Etika

❌ "婚姻必失敗" — JANGAN
✅ "perlu effort komunikasi lebih untuk membangun harmoni"

❌ "聚少離多" (bersama sedikit, berpisah lebih banyak)
✅ "lifestyle yang mungkin sering jauh secara fisik (kerja terpisah, dll)"

❌ "白頭偕老" jangan menjanjikan absolut
✅ "potensi membangun hubungan jangka panjang yang baik"

## Sumber

- 《三命通會·論支神類神》
- 《淵海子平·論刑沖合害》
- 林文榮《八字精論》(Taiwan)
