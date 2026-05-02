# Format Output Software 星僑 V2.6

Reference untuk mengenali struktur layar output software ramalan
**四柱論命附加紫微斗數 V2.6** dari 星僑 / NCC Taiwan.

## Identifikasi Software

Setiap foto memiliki **header tetap** di bagian atas:

```
[星僑]   四柱論命附加紫微斗數  V2.6  [星僑]
A:輸入生日  B:專家命盤  C:詳細解說  D:流年判斷  E:自動列印  F:參數設定
```

Latar layar = **biru gelap** (#000080 atau #001a4d).
Teks utama = **kuning/cyan/hijau/putih** (warna bermakna).
Frame border = **cyan terang** kotak rounded.

Author info (di footer beberapa halaman):
```
台內著字: 第72685號     版權所有, 翻版必究
著作: 陳恩國          地址: 桃園縣龜山鄉頂湖路16-3號
程式設計: 陳慶鴻       電話: (03)3285686-7  FAX: (03)3286557
```

## Identifikasi Subjek (di footer setiap layar)

```
姓名: [NAMA] [男/女] 農曆民國 [YY] 年 [MM] 月 [DD] 日 [HH] 時 [mm] 分
```

**Konversi tahun**: 民國 + 1911 = 西元
- 民國 47年 = 1958
- 民國 70年 = 1981
- 民國 107年 = 2018

## Layar Chart Utama (BaZi 四柱)

Dikenali dari **tabel 4 kolom besar** dengan header:
```
[星僑]    命   論   柱   四    [星僑]
```

Kolom (dari kanan ke kiri, gaya tradisional):
1. **年柱** (Year Pillar) — kanan paling jauh
2. **月柱** (Month Pillar)
3. **日柱** (Day Pillar) — **日主** highlighted
4. **時柱** (Hour Pillar) — kiri paling jauh

Setiap kolom punya baris:
- 天干 (Heavenly Stem) — atas
- 地支 (Earthly Branch)
- 藏干 (Hidden Stems)
- 十神 (Ten Gods)
- 納音 (Sound Element)

Sisi kiri layar:
- **先天體檢** — Body health check (organ scoring 0-9)
- **喜用神** (Lucky Element) — di pojok kiri bawah
- **忌神/仇神** (Unlucky Element)

Sisi kanan layar:
- **西元 [YYYY] 年** (Western year)
- **國曆民國 [YY] 年 [M] 月 [D] 日**
- **農曆民國 [YY] 年 [M] 月 [D] 日**
- **[H] 時 [m] 分 生**
- **星期 [hari]**
- **屬 [shio]**

Bagian tengah:
- **命宮** (Life Palace position)
- **日主旺度** dengan angka +X.XXX / -X.XXX
  - Positif = day master strong / 旺
  - Negatif = day master weak / 弱
- **大運** table — 8-10 cycles 10-tahunan

## Layar Chart Zi Wei (紫微斗數)

Dikenali dari **grid 12 kotak palace** (4×4 dengan tengah kosong).
Layout standar:

```
┌──────┬──────┬──────┬──────┐
│ 巳宮 │ 午宮 │ 未宮 │ 申宮 │
├──────┼──────┴──────┼──────┤
│ 辰宮 │             │ 酉宮 │
├──────┤  Info Box   ├──────┤
│ 卯宮 │ (Subject)   │ 戌宮 │
├──────┼──────┬──────┼──────┤
│ 寅宮 │ 丑宮 │ 子宮 │ 亥宮 │
└──────┴──────┴──────┴──────┘
```

Tiap kotak palace berisi:
- Nama palace (財帛, 子女, 夫妻, 命宮, dll)
- 地支 (子, 丑, 寅, ...)
- Bintang utama (紫微, 天府, 太陽, 武曲, dll)
- Bintang minor (左輔, 右弼, 文昌, 文曲, dll)
- 化祿/化權/化科/化忌 marker
- 大限 range (e.g., 23-32, 33-42)
- 小限 number (1-12)

Info Box tengah berisi:
- 西元 + 國曆 + 農曆 birth info
- 命主, 身主 (Life Lord, Body Lord stars)
- 命宮 (Life Palace 地支)
- 身宮 (Body Palace 地支)
- 五行局 (Five Elements School: 水二局/木三局/金四局/土五局/火六局)
- 子斗時君 (Time Lord)

## Layar Detail Interpretasi

Dikenali dari **header tanda kurung [XXX]** di tengah layar:

```
─────────────────  [ 性 情 ]  ─────────────────
```

Diikuti paragraf interpretasi (warna hijau untuk umum, kuning/merah untuk
peringatan).

### 17 Kategori Header

| Hanzi | Pinyin | Indonesia | Bagian |
|-------|--------|-----------|--------|
| 【性情】 | Xìng Qíng | Kepribadian | BaZi |
| 【全局總論】 | Quánjú Zǒnglùn | Ringkasan Menyeluruh | BaZi |
| 【神煞】 | Shén Shà | Bintang Nasib | BaZi |
| 【財富】 | Cái Fù | Kekayaan | BaZi |
| 【婚配】 | Hūn Pèi | Kompatibilitas Jodoh | BaZi |
| 【事業】 | Shì Yè | Karir/Profesi | BaZi |
| 【陽宅】 | Yáng Zhái | Feng Shui Rumah | BaZi-derived |
| 【命宮】 | Mìng Gōng | Palace Diri | Zi Wei |
| 【兄弟】 | Xiōng Dì | Saudara | Zi Wei |
| 【夫妻】 | Fū Qī | Pasangan | Zi Wei |
| 【子女】 | Zǐ Nǚ | Anak | Zi Wei |
| 【財帛】 | Cái Bó | Rezeki Harian | Zi Wei |
| 【疾厄】 | Jí È | Kesehatan | Zi Wei |
| 【遷移】 | Qiān Yí | Perpindahan | Zi Wei |
| 【僕役】 | Pú Yì | Bawahan/Teman | Zi Wei |
| 【官祿】 | Guān Lù | Karir Formal | Zi Wei |
| 【田宅】 | Tián Zhái | Properti | Zi Wei |
| 【福德】 | Fú Dé | Berkah/Karma | Zi Wei |
| 【父母】 | Fù Mǔ | Orangtua | Zi Wei |

(19 total dengan 父母, 福德, dll. Total kategori bisa 17-20 tergantung versi.)

## Bookmark/Marker di Foto

Di bagian bawah layar selalu ada bar status:
```
[P]:列表  [Esc]:結束  [↓]:下一行  [↑]:上一行  [PgUp]:上一頁  [PgDn]:下一頁
[英數]  [半形]                                                  >倚天<
```

`>倚天<` di pojok kanan bawah = mode font Eten (DOS Chinese system).

## Aturan Pembacaan Foto

**Foto blur/buram?**
- Cek dulu apakah header `【XXX】` masih bisa dibaca → identifikasi kategori
- Coba ekstrak setidaknya keyword utama (warna merah biasanya kalimat penting)
- Tag bagian tidak terbaca dengan `[?]`

**Karakter tidak standar?**
- Software ini pakai **Hanzi Tradisional** (繁體中文)
- Bukan simplified — jangan auto-convert
- Beberapa karakter klasik mungkin gak ada di Unicode standar — fallback ke
  variant terdekat

**Multiple foto kategori sama?**
- Kategori panjang (seperti 事業 atau 命宮 detail) bisa pecah ke 2-3 layar
  karena layar laptop kecil
- Cek nomor `>下一頁<` atau scroll indicator
- Gabungkan transkrip kalau memang lanjutan

## Urutan Halaman Tipikal

Software 星僑 V2.6 menampilkan output berurutan saat user tekan PgDn:

```
1. Chart utama 四柱
2. Chart 紫微斗數 (kalau bundle V2.6)
3. 性情
4. 全局總論
5. 神煞
6. 財富
7. 婚配
8. 事業
9. 陽宅
10. 命宮 detail
11. 兄弟 detail
12. 夫妻 detail
... (12 palaces sampai 父母)
20. (kadang ada 大運/流年 detail tambahan)
```

Jadi kalau user kasih ~17-19 foto, kemungkinan urutan capture mengikuti ini.

## Tips Klasifikasi Cepat

| Petunjuk visual | Kategori kemungkinan |
|-----------------|----------------------|
| Tabel 4 kolom besar | 四柱 chart |
| Grid 4×4 | 紫微 chart |
| Banyak baris paragraf hijau | 性情/全局總論/dll teks |
| List dengan bullet ◎ | 事業 (industries) atau 陽宅 (directions) |
| Nama bintang dalam tanda kurung 【】 di tabel | 神煞 listing |
| Mention 配相 dan nama hewan | 婚配 |
| Mention 方/向/位 | 陽宅 |
| Mention 主星/三方四正 | Zi Wei palace detail |

## Referensi Software

- Vendor: ncc.com.tw / nccsoft.com (Taiwan)
- Author 陳恩國 — content writer
- Programmer 陳慶鴻
- Versi V2.6 = bundle 四柱 + 紫微
- Tahun rilis: ~1995-2000 (era DOS Eten Chinese)
- Pengganti modern: NCC Pro, 星僑命盤 App (iOS/Android)
