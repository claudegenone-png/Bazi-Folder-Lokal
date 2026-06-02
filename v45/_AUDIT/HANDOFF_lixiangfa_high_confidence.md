# HANDOFF — Re-validate & Fix `lixiangfa.md` (4 HIGH confidence findings)

> Untuk main window agent. External auditor (window terpisah) sudah ekstrak foto-only HIGH confidence. Tugasmu: validasi independen baca foto sendiri, lalu fix kalau setuju.

## ATURAN UNTUK MU (main agent)

1. **Baca foto sendiri** untuk tiap finding, jangan trust audit ini buta.
2. **DILARANG pakai rumus BaZi/陰陽/aturan klasik** untuk derive nilai. Hanya copy-translate teks foto.
3. Setuju → fix MD `C:\Users\sukam\OneDrive\Documents\Ramalan\v45\data\subjects\lixiangfa.md`.
4. Tidak setuju → STOP, lapor disagreement dengan quote foto verbatim, JANGAN fix.
5. Setelah fix semua, append ke `## CATATAN`:
   ```
   - 2026-05-08: 4 high-confidence corrections applied per HANDOFF audit (gender_hz, gushuyun bait 4, liu_nian 2030 hallucination, liu_nian 神煞 + bulan-larangan).
   ```
6. Re-build PDF: `cd C:\Users\sukam\OneDrive\Documents\Ramalan\v45 && python build_pdf.py lixiangfa`.

---

## FINDING 1 — `gender_hz` salah

**Path foto sumber**:
- `C:\Users\sukam\OneDrive\Documents\Ramalan\foto\08-05-2026\Li Xiang Fa\new bazi.jpeg` (BaZi grid utama, pojok kiri-atas)
- `C:\Users\sukam\OneDrive\Documents\Ramalan\foto\08-05-2026\Li Xiang Fa\WhatsApp Image 2026-05-08 at 06.17.03.jpeg` (palace summary, header bar)

**MD saat ini**:
```
- gender_hz: 陽男
```

**Foto verbatim**:
- `new bazi.jpeg` pojok kiri-atas: **男陰**
- `06.17.03` header bar: **陰男**

**Aksi fix**:
```
- gender_hz: 陰男
```

---

## FINDING 2 — `gushuyun_paragraf_hz` bait keempat hilang

**Path foto sumber**: `C:\Users\sukam\OneDrive\Documents\Ramalan\foto\08-05-2026\Li Xiang Fa\WhatsApp Image 2026-05-08 at 06.17.09 (2).jpeg`

**MD saat ini** (section `## DATA_EXTRA` → `### 古書云 — kutipan klasik tentang Day Master`):
```
- gushuyun_paragraf_hz: 三命通會註：戊己日干尋水木，柱中原有還為福，運臨北野及東方，德潤身兮富潤屋。滴天髓：己土卑溼，中正蓄藏，不愁木盛，不畏水狂，火少火晦，金多金光，若要物旺，宜助宜幫。詩云：五月炎炎火正升，六陽氣盡一陰生，庚金失位金無用，己土歸垣祿有成，甲子齊來能戰煞，戊寅同見越光明，東南正是身強地，西北休囚己喪刑。
```

**Foto verbatim**: foto punya 4 bait. MD hanya simpan 3. Bait keempat hilang:
> 土田圍繞四維，坤深能為萬物基，水金旺處身還弱，火土功成局最奇，失令豈能埋劍戰，得時方可用銳基，漫誇印旺兼多合，可遇沖刑總不宜。

**Aksi fix**: append bait keempat ke `gushuyun_paragraf_hz`. Hasil akhir:
```
- gushuyun_paragraf_hz: 三命通會註：戊己日干尋水木，柱中原有還為福，運臨北野及東方，德潤身兮富潤屋。滴天髓：己土卑溼，中正蓄藏，不愁木盛，不畏水狂，火少火晦，金多金光，若要物旺，宜助宜幫。詩云：五月炎炎火正升，六陽氣盡一陰生，庚金失位金無用，己土歸垣祿有成，甲子齊來能戰煞，戊寅同見越光明，東南正是身強地，西北休囚己喪刑。土田圍繞四維，坤深能為萬物基，水金旺處身還弱，火土功成局最奇，失令豈能埋劍戰，得時方可用銳基，漫誇印旺兼多合，可遇沖刑總不宜。
```

Update juga `gushuyun_terjemahan_id` — append translate literal bait keempat:
> Tanah ladang mengelilingi empat penjuru, Kun yang dalam mampu jadi dasar segala benda; di tempat air dan logam bersamaan kuat, badan tetap lemah; bila api dan tanah bersatu sempurna, formasinya paling istimewa. Kehilangan musim mana bisa mengubur pedang berperang; saat dapat momentum, baru bisa pakai pisau tajam. Jangan terlalu bangga dengan 印 yang banyak gabungan, kalau ketemu 沖 atau 刑 semua tidak baik.

(Atau translate literal versi kau sendiri — yang penting append, jangan kosongkan.)

---

## FINDING 3 — `liu_nian_predictions` 2030 invent "api dan air"

**Path foto sumber**: `C:\Users\sukam\OneDrive\Documents\Ramalan\foto\08-05-2026\Li Xiang Fa\WhatsApp Image 2026-05-08 at 06.17.10 (3).jpeg`

**MD saat ini**:
```
- tahun 2030 (usia 34, [[庚戌]]): Apa yang dipikirkan dan dikeluarkan tahun ini sebanding dengan hasil. Bisa mendapatkan bantuan dari saudara dan teman dekat. Emosi tidak stabil, banyak perubahan posisi atau pekerjaan. Foto福德 menyalakan rezeki tambahan; hati-hati api dan air. Hindari bulan 4-7-8 untuk keputusan besar.
```

**Foto verbatim** (06.17.10(3) judul 【流年】 西元2030年 民國119年 歲次庚戌 34歲):
```
今年用腦所想出來的事物，表面上能與金錢成對比。
能得到兄弟朋友的幫助，實質上可以達到相當的理想。
對心情有所牽制，心情也不穩定。
事業會有所變動或職位上有所變動。
福德：福德命中逢，加官進祿修，田園多創置，萬事好求謀。
無常：運逢無常流年星，恐有不測事相生，孝服運待秋堅去，脫災無事心自明。恐有疾病，破財過運，忌四七八月。當防水火。
努力會得到利或獲得貴人幫忙之先兆。
```

**Catatan penting**: foto sebenarnya **ADA** kalimat "**當防水火**" (waspada air dan api) — di akhir paragraf 無常. Jadi "api dan air" di MD **sebenarnya BENAR** secara content, hanya kurang konteks 神煞 sumbernya.

> ⚠️ External auditor sebelumnya keliru bilang ini halusinasi. Setelah re-baca foto teliti, ternyata "當防水火" memang ada di foto. Yang **kurang lengkap** di MD adalah:
> - Nama 神煞: **福德** (positif: 加官進祿 = naik jabatan + rezeki) dan **無常** (negatif: 疾病 + 破財)
> - Konteks "當防水火" datang dari bintang 無常, bukan generic warning
> - Foto sebut "**加官進祿**" (promotion + income) — MD soft-translate jadi "rezeki tambahan", undersell

**Aksi fix**: rewrite 2030 entry supaya capture nama 神煞 + konten lebih akurat:
```
- tahun 2030 (usia 34, [[庚戌]]): Pikiran dan usaha tahun ini sebanding dengan hasil keuangan. Dapat bantuan dari saudara dan teman dekat. Emosi tidak stabil, ada perubahan posisi atau pekerjaan. Bintang [[福德]] menyalakan promosi jabatan dan rezeki tambahan, peluang menambah aset properti, segala urusan mudah berhasil. Bintang [[無常]] berisiko penyakit dan kehilangan uang — waspada air dan api (當防水火). Hindari bulan 4, 7, 8. Kerja keras dapat hasil dan bantuan orang penting.
```

---

## FINDING 4 — `liu_nian_predictions` 2026-2029 hilang nama 神煞 + bulan-larangan

**Path foto sumber**:
- 2026: `WhatsApp Image 2026-05-08 at 06.17.10.jpeg` — 西元2026年 歲次丙午 30歲
- 2027: `WhatsApp Image 2026-05-08 at 06.17.10 (1).jpeg` — 歲次丁未 31歲
- 2028: `WhatsApp Image 2026-05-08 at 06.17.10 (2).jpeg` — 歲次戊申 32歲
- 2029: `WhatsApp Image 2026-05-08 at 06.17.10 (3).jpeg` — Wait ini sebenarnya 2029. **Verifikasi ulang nama file mana untuk tahun mana** — saya bisa salah mapping di list ini.

**Foto verbatim per tahun** (HZ key phrases):

**2026 丙午 30歲**:
- 死符 in 命: 死符入命中，辛服有悲傷，父母兄弟剋，祈神免災殃
- 暗曜
- 易遭官災、刑罰、訴訟、受傷、精神上的痛苦
- 忌二五八或十二月

**2027 丁未 31歲**:
- 歲破: 歲破命中逢，破財不可當，六親防有民，作福保安康
- 太陰: 流年運逢太陰星，主有喜事來相生，求財享通人決意
- 忌三六九或十二月

**2028 戊申 32歲**:
- 龍德: 龍德入命來，四季得錢財，在家多吉利，出外無衰災
- 天掃: 流年天掃星里逢運，主有孝服亂紛紛，若得貴人喜事到，無災須防鬼賊吞
- 忌一四七或十二月

**2029 己酉 33歲**:
- 白虎: 白虎臨岩運，口舌兼破財，前門虎走，後門進狼來
- 天喜: 流年天喜星相逢，家有喜事迎春風，謀財事多得意，血刃之災須知防
- 忌四七或十一月

**MD saat ini**: predictions soft, generalize, hilangkan nama 神煞 + bulan spesifik. Salah satu contoh — MD 2028:
```
- tahun 2028 (usia 32, [[戊申]]): Apa yang dikeluarkan tahun ini sebanding dengan hasil keuangan. Bisa berpikir dan menghasilkan ide-ide cemerlang, harus memanfaatkan momentum. Banyak ide untuk diwujudkan, hati-hati tidak terlalu spekulatif. Hindari masalah dengan rekan kerja dan saudara. **Hati-hati cedera kepala dan tangan.**
```

Catatan: "cedera kepala dan tangan" di 2028 — **TIDAK ADA di foto 2028**. Itu ada di 2027 atau 2029 (foto 2029 sebut 血刃之災). Salah mapping.

**Aksi fix**: rewrite 4 entry (2026-2029) dengan format konsisten:
- Sebut nama 神煞 utama tahun (positif & negatif)
- Capture bulan-larangan spesifik
- Capture warning unik (官災/血刃/破財/dst)
- Hapus klaim yang tidak ada di foto tahun tsb

Contoh rewrite 2028:
```
- tahun 2028 (usia 32, [[戊申]]): Hasil pikiran dan kerja tahun ini sebanding dengan keuangan. Dapat bantuan saudara dan teman dekat. Bintang [[龍德]] membawa rezeki di empat musim, di rumah banyak hoki, ke luar tanpa bencana. Bintang [[天掃]] berisiko duka cita berturut-turut — kalau dapat bantuan orang penting, peristiwa baik datang, hati-hati pencurian. Hindari bulan 1, 4, 7, 12.
```

Format yang sama untuk 2026, 2027, 2029. **Pastikan tiap warning hanya muncul di tahun yang foto sebenarnya menyebut** — jangan cross-contaminate antar tahun.

---

## CHECKLIST EKSEKUSI

- [ ] Finding 1 — gender_hz: baca foto, validasi, fix kalau setuju.
- [ ] Finding 2 — gushuyun bait 4: baca foto, validasi text bait keempat, append.
- [ ] Finding 3 — 2030 sudah benar "當防水火" tapi kurang konteks 神煞: rewrite.
- [ ] Finding 4 — 2026-2029 + cross-contamination "cedera kepala": rewrite per tahun pakai foto masing-masing, **tidak boleh cross-contamination**.
- [ ] Append catatan ke `## CATATAN`.
- [ ] `python build_pdf.py lixiangfa` — re-build PDF.
- [ ] Verifikasi PDF page Da Yun + page 古書云 + page Liu Nian + halaman ID footer (gender label) tampil benar.
- [ ] Lapor user: ringkasan diff + path PDF baru.

Kalau ada **disagreement** dengan finding manapun, STOP, jangan fix, lapor user dengan quote foto verbatim.
