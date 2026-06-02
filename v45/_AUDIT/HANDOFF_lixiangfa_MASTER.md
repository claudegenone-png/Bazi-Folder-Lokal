# MASTER HANDOFF — `lixiangfa.md` perbaikan (FOTO-ONLY, no derive)

> **Untuk main window agent.** Konsolidasi semua finding eksternal auditor (window terpisah) yang murni foto-only — tanpa rumus, tanpa interpretasi, tanpa derive. File ini supersede 2 handoff sebelumnya (`HANDOFF_lixiangfa_yangzhai.md` dan `HANDOFF_lixiangfa_high_confidence.md`).

---

## ATURAN UNTUK MU (main agent)

1. **Baca foto sendiri** untuk tiap finding. Jangan trust audit ini buta.
2. **Foto path**: gunakan `C:\Users\sukam\OneDrive\Documents\Ramalan\foto\08-05-2026\Li Xiang Fa\*.jpeg` (folder ORIGINAL, **bukan** `1_prepped/` — folder prepped lebih blur, lihat `DECISION_prep_photos_strategy.md`).
3. **DILARANG**:
   - Pakai rumus BaZi/ZW/Yang Zhai/陰陽五行/aturan klasik untuk derive nilai
   - Cross-validation antar field MD untuk simpulkan benar/salah
   - Tebak hanzi yang ambigu — kalau ragu, STOP dan flag
4. Setuju dengan finding → fix MD `C:\Users\sukam\OneDrive\Documents\Ramalan\v45\data\subjects\lixiangfa.md`
5. Tidak setuju → STOP, lapor disagreement dengan quote foto verbatim, JANGAN fix
6. Setelah semua fix, append ke `## CATATAN`:
   ```
   - 2026-05-08: master corrections applied per HANDOFF_lixiangfa_MASTER (gender_hz, yang_zhai zones+paragraf, gushuyun bait 4, liu_nian 2026-2030, marriage 次吉 clause).
   ```
7. Re-build PDF: `cd C:\Users\sukam\OneDrive\Documents\Ramalan\v45 && python build_pdf.py lixiangfa`
8. Lapor user: ringkasan diff + path PDF baru.

---

## SUMMARY TABEL FINDING

| # | Field | Confidence | Foto sumber |
|---|---|---|---|
| 1 | `gender_hz` | HIGH | new bazi.jpeg + 06.17.03.jpeg |
| 2 | Yang Zhai zones (6 zone) + paragraf | HIGH | 06.17.05.jpeg |
| 3 | `gushuyun_paragraf_hz` bait 4 | HIGH | 06.17.09 (2).jpeg |
| 4 | `liu_nian_predictions` 2026 | HIGH | 06.17.10.jpeg |
| 5 | `liu_nian_predictions` 2027 | HIGH | 06.17.10 (1).jpeg |
| 6 | `liu_nian_predictions` 2028 + cross-contamination | HIGH | 06.17.10 (2).jpeg |
| 7 | `liu_nian_predictions` 2029 | HIGH | 06.17.10 (3).jpeg (verifikasi mapping) |
| 8 | `liu_nian_predictions` 2030 | HIGH | 06.17.10 series (verifikasi tahun) |
| 9 | Marriage 次吉 clause | HIGH | 06.17.05 (2).jpeg |

---

## FINDING 1 — `gender_hz` salah

**Foto verbatim**:
- `new bazi.jpeg` pojok kiri-atas: **男陰**
- `06.17.03.jpeg` header bar: **陰男**

**MD saat ini**: `gender_hz: 陽男`

**Aksi fix**: ubah ke `gender_hz: 陰男`

---

## FINDING 2 — Yang Zhai (6 zones + paragraf)

**Foto verbatim** (`06.17.05.jpeg`):
```
○震卦
◎宅宜坐北向南或坐南向北大吉。
門路宜開南方、北方、東南方吉。
爐灶宜安西方向東或西北方向東南。
房間宜安南方、北方、東方、東南方。
床位宜安東方、東南方、南方、北方吉。
神位宜安南方或北方、東方及本年大利方吉。
坑廁宜安於東北方、西北方、西方、西南方。
```

### Zones — fix 6 entries:

| Zone | MD pills sekarang | Aksi fix (foto verbatim) |
|---|---|---|
| Pintu Utama (門路) | `南 S` | Pills: `南 S / 北 U / 東南 TG`. Note: "Pintu utama: Selatan, Utara, atau Tenggara." |
| Kamar Tidur (房間) | `東 T` | Pills: `南 S / 北 U / 東 T / 東南 TG`. Note: "Kamar di Selatan, Utara, Timur, atau Tenggara." |
| Dapur / Kompor (爐灶) | `西 B` | Pills: `西→東 / 西北→東南`. Note: "Kompor: duduk Barat menghadap Timur, atau duduk Barat Laut menghadap Tenggara." |
| Kamar Mandi (坑廁) | `⚠ Hindari, 西南 BD` | Pills: `東北 TL / 西北 BL / 西 B / 西南 BD`. Headline: `✓ OK`. Note: "Toilet baik di Timur Laut, Barat Laut, Barat, atau Barat Daya." |
| Ruang Kerja | `東南 TG` (HALUSINASI — foto tidak sebut zona ini) | **HAPUS** entry "Ruang Kerja". Ganti dengan zona **Ranjang (床位)** yang foto sebut: pills `東 T / 東南 TG / 南 S / 北 U`. Note: "Ranjang baik di Timur, Tenggara, Selatan, atau Utara." |
| Altar / Sembah (神位) | `東北 TL` (note "TL atau BL") | Pills: `南 S / 北 U / 東 T`. Note: "Altar baik di Selatan, Utara, atau Timur. Plus arah hoki tahun ini (本年大利方)." |

### Paragraf — hapus halusinasi

**MD saat ini** (paragraf):
> "Hindari kamar tidur di sektor Barat Daya yang melambangkan stagnasi."

Foto **tidak menyebut** larangan kamar tidur Barat Daya. **HAPUS kalimat ini.**

### Yang sudah benar (jangan diubah)
- Trigram 震 ✓
- "Rumah duduk Utara menghadap Selatan, atau duduk Selatan menghadap Utara" ✓ (foto: 宅宜坐北向南或坐南向北大吉)
- Pintu Selatan partial benar (foto sebut S/U/TG, MD pintu Selatan termasuk dalam set)

---

## FINDING 3 — `gushuyun_paragraf_hz` bait keempat hilang

**Foto verbatim** (`06.17.09 (2).jpeg`): foto punya 4 bait. MD hanya 3.

**Bait keempat yang hilang**:
> 土田圍繞四維，坤深能為萬物基，水金旺處身還弱，火土功成局最奇，失令豈能埋劍戰，得時方可用銳基，漫誇印旺兼多合，可遇沖刑總不宜。

**Aksi fix**:
- Append bait 4 ke `gushuyun_paragraf_hz` (di akhir, setelah "西北休囚己喪刑。")
- Append translate literal ke `gushuyun_terjemahan_id`. Saran translate (boleh kau revisi):
  > Tanah ladang mengelilingi empat penjuru, Kun yang dalam mampu jadi dasar segala benda; di tempat air dan logam bersamaan kuat, badan tetap lemah; bila api dan tanah bersatu sempurna, formasinya paling istimewa. Kehilangan musim mana bisa mengubur pedang berperang; saat dapat momentum, baru bisa pakai pisau tajam. Jangan terlalu bangga dengan 印 yang banyak gabungan, kalau ketemu 沖 atau 刑 semua tidak baik.

---

## FINDING 4 — `liu_nian_predictions` 2026-2030 perbaikan

**Aturan rewrite**:
- Tiap entry harus **sebut nama 神煞** (positif & negatif) yang foto sebut spesifik di tahun itu
- Capture **bulan-larangan** spesifik per tahun
- Capture warning unik (官災/血刃/破財/dll)
- **Tidak boleh cross-contamination** — warning di tahun A jangan masuk tahun B
- Dilarang invent klaim yang tidak ada di foto

### 2026 (丙午, 30歲) — foto `06.17.10.jpeg`

**Foto verbatim key phrases**:
- 死符: 死符入命中，辛服有悲傷，父母兄弟剋，祈神免災殃
- 暗曜
- 易遭官災、刑罰、訴訟、受傷、精神上的痛苦
- 忌二五八或十二月

**Aksi fix**: rewrite supaya capture **死符** + **暗曜** + warning 官災/刑罰/訴訟 + **bulan 2/5/8/12**.

### 2027 (丁未, 31歲) — foto `06.17.10 (1).jpeg`

**Foto verbatim**:
- 歲破: 歲破命中逢，破財不可當，六親防有民，作福保安康
- 太陰: 流年運逢太陰星，主有喜事來相生，求財享通人決意
- 忌三六九或十二月
- 已婚者夫妻間會問感情，未婚者會走感情

**Aksi fix**: capture **歲破** (warning 破財 berat) + **太陰** + bulan 3/6/9/12 + romansa/perselisihan pasangan.

### 2028 (戊申, 32歲) — foto `06.17.10 (2).jpeg`

**Foto verbatim**:
- 龍德: 龍德入命來，四季得錢財，在家多吉利，出外無衰災
- 天掃: 流年天掃星里逢運，主有孝服亂紛紛，若得貴人喜事到，無災須防鬼賊吞
- 忌一四七或十二月

**MD saat ini** ada klaim "**Hati-hati cedera kepala dan tangan**" — **TIDAK ADA** di foto 2028. Itu cross-contamination dari 2029 (foto 2029 sebut 血刃之災). **HAPUS** dari 2028.

**Aksi fix**: capture **龍德** (4 musim rezeki) + **天掃** (孝服 risk) + bulan 1/4/7/12. Hapus "cedera kepala dan tangan".

### 2029 (己酉, 33歲) — foto `06.17.10 (3).jpeg` (verifikasi nama file)

**Foto verbatim**:
- 白虎: 白虎臨岩運，口舌兼破財，前門虎走，後門進狼來
- 天喜: 流年天喜星相逢，家有喜事迎春風，謀財事多得意，血刃之災須知防
- 忌四七或十一月
- 但卻不適宜當領導階層

**Aksi fix**: capture **白虎** (口舌+破財) + **天喜** (家有喜事) + warning **血刃** + bulan 4/7/11 + "tidak cocok memimpin".

### 2030 (庚戌, 34歲) — foto perlu verifikasi nama file (di series 06.17.10 atau 06.17.11)

**Foto verbatim**:
- 福德: 福德命中逢，加官進祿修，田園多創置，萬事好求謀
- 無常: 運逢無常流年星，恐有不測事相生，孝服運待秋堅去，脫災無事心自明。恐有疾病，破財過運，忌四七八月。當防水火。

**Catatan koreksi**: external auditor sebelumnya keliru bilang MD "api dan air" halusinasi. Setelah re-baca teliti, foto **memang ada** "**當防水火**" (waspada air dan api) dari bintang 無常. Yang **kurang lengkap** adalah:
- Nama 神煞 **福德** + **無常** (MD hilangkan)
- "**加官進祿**" (promotion + income) — MD soft-translate jadi "rezeki tambahan", undersell

**Aksi fix**: capture **福德** (加官進祿/田園多創置) + **無常** (疾病+破財) + 當防水火 + bulan 4/7/8.

---

## FINDING 5 — Marriage 次吉 clause hilang

**Foto verbatim** (`06.17.05 (2).jpeg`):
```
宜：配相鼠、蛇、雞大吉其他生相次吉。
天作良緣，必定家聲克振，富貴門楣，表素淑禹，家勢盛大，安樁吉慶美德終世。
```

**MD saat ini**:
- `marriage_cocok: 鼠, 蛇, 雞` (= 大吉) ✓ benar
- `marriage_hindari: 龍, 馬, 羊, 狗` ✓ benar
- **Tidak ada field** untuk clause "其他生相次吉" (shio lainnya = cukup baik)

**Aksi fix**: tambah field di MD:
```
- marriage_other_label_hz: 其他生相次吉
- marriage_other_label_id: shio lainnya cukup baik (次吉)
```

**JANGAN** list nama-nama 次吉 (牛/虎/兔/猴/豬) sebagai klaim foto — itu derived (12 shio - 3 大吉 - 4 大凶), bukan verbatim foto.

---

## CHECKLIST EKSEKUSI

### Validasi
- [ ] Baca foto path original `Li Xiang Fa/.jpeg`, bukan prepped.
- [ ] Untuk tiap finding, baca foto sumber sendiri, OCR cocok dengan teks verbatim di handoff (atau flag perbedaan).

### Fix
- [ ] **Finding 1** — `gender_hz` ke `陰男`
- [ ] **Finding 2** — Yang Zhai 6 zones rewrite + hapus halusinasi paragraf "Hindari kamar tidur BD"
- [ ] **Finding 3** — gushuyun bait 4 append (hz + id)
- [ ] **Finding 4** — liu_nian 2026, 2027, 2028 (hapus cross-contamination), 2029, 2030
- [ ] **Finding 5** — marriage_other_label_hz + _id

### Re-build & verifikasi
- [ ] Append catatan ke `## CATATAN` MD.
- [ ] `python build_pdf.py lixiangfa`
- [ ] Verifikasi PDF page Yang Zhai, gushuyun, liu_nian, marriage, ID footer (gender label) tampil benar.
- [ ] Lapor user: ringkasan diff sebelum/sesudah + path PDF baru.

### Disagreement protocol
Kalau ada finding yang **tidak setuju** (foto bilang lain dari yang handoff klaim):
- STOP, **JANGAN** fix.
- Lapor user dengan: nama foto, lokasi spesifik di foto, teks hz verbatim yang KAU baca, vs teks handoff klaim.
- Tunggu user putuskan.

---

## FINDING DI LUAR SCOPE HANDOFF (jangan disentuh tanpa instruksi terpisah)

**MEDIUM/LOW confidence** — eksternal auditor pernah flag tapi belum confident foto-only:
- `shi_shen_per_pilar_jam` (傷官 vs 偏官) — hanzi mirip, butuh foto resolusi tinggi
- ZW palace stars per palace (12 palace) — CRT chart padat, dual-pass belum dilakukan
- ZW palace insight paragraphs (Palace Detail 1/2/3)

Ini akan ditangani di handoff terpisah setelah re-audit pakai foto original (post-Opsi A switch).
