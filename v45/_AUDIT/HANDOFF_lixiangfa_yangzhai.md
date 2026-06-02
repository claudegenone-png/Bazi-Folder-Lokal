# HANDOFF — Re-validate & Fix `lixiangfa.md` section Yang Zhai

> Untuk main window agent. External auditor (window terpisah) sudah ekstrak foto-only. Tugasmu: **validasi independen** dengan baca foto sendiri, lalu fix kalau setuju.

## ATURAN UNTUK MU (main agent)

1. **Baca foto sendiri**, jangan trust audit ini buta. Path foto: `C:\Users\sukam\OneDrive\Documents\Ramalan\foto\08-05-2026\Li Xiang Fa\WhatsApp Image 2026-05-08 at 06.17.05.jpeg` (original) atau `C:\Users\sukam\OneDrive\Documents\Ramalan\foto\08-05-2026\1_prepped\WhatsApp Image 2026-05-08 at 06.17.05.jpg` (prepped).
2. **DILARANG pakai rumus Yang Zhai / Ba Zhai / 震卦 mapping** untuk derive arah hunian. Hanya copy-translate teks foto.
3. Kalau setuju dengan finding external auditor → fix MD di `C:\Users\sukam\OneDrive\Documents\Ramalan\v45\data\subjects\lixiangfa.md` section `### Yang Zhai (Feng Shui Hunian)`.
4. Kalau **tidak setuju** → tulis di chat alasan + quote foto verbatim yang kau baca, JANGAN fix.
5. Setelah fix, append baris ke `## CATATAN`:
   ```
   - Yang Zhai zones: dikoreksi 2026-05-08 ulang sesuai foto 06.17.05 verbatim (lihat HANDOFF audit log).
   ```

---

## TEKS FOTO 【陽宅】 verbatim (yang external auditor baca)

```
○震卦
◎宅宜坐北向南或坐南向北大吉。門路宜開南方、北方、東南方吉。爐灶宜安西方向東或西北方向東南。房間宜安南方、北方、東方、東南方。床位宜安東方、東南方、南方、北方吉。神位宜安南方或北方、東方及本年大利方吉。坑廁宜安於東北方、西北方、西方、西南方。
```

Verifikasi dulu kau baca yang sama. Kalau beda → flag.

---

## TEMUAN EXTERNAL AUDITOR (yang harus kau validasi)

### ❌ HARD MISMATCH — perlu fix

| # | Zone MD saat ini | MD klaim | Foto verbatim | Aksi fix |
|---|---|---|---|---|
| 1 | Kamar Mandi | `headline: "⚠ Hindari"`, `pills: 西南 BD` | `坑廁宜安於東北方、西北方、西方、西南方` (BD justru direkomendasikan) | Ubah headline jadi `✓ OK`, pills jadi `東北 TL / 西北 BL / 西 B / 西南 BD`, note ganti jadi "Toilet baik diletakkan di Timur Laut, Barat Laut, Barat, atau Barat Daya." |
| 2 | Altar / Sembah | `pills: 東北 TL`, note "TL atau BL" | `神位宜安南方或北方、東方及本年大利方吉` | Ubah pills jadi `南 S / 北 U / 東 T`, note ganti jadi "Altar baik di Selatan, Utara, atau Timur. Plus arah hoki tahunan (本年大利方)." |
| 3 | Ruang Kerja | `pills: 東南 TG` | Foto **tidak menyebut** zona "ruang kerja / 書房 / 工作室" sama sekali | **Hapus** entry "Ruang Kerja" dari `zones:`. Atau, kalau template butuh 6 zona, ganti dengan zona yang foto sebenarnya sebut: **Ranjang (床位)**. |

### ⚠️ INCOMPLETE — perlu lengkapi

| # | Zone | MD pills sekarang | Foto verbatim | Aksi fix |
|---|---|---|---|---|
| 4 | Pintu Utama | `南 S` | `門路宜開南方、北方、東南方` | Pills jadi `南 S / 北 U / 東南 TG`, note: "Pintu utama: Selatan, Utara, atau Tenggara." |
| 5 | Kamar Tidur (= 房間) | `東 T` | `房間宜安南方、北方、東方、東南方` | Pills jadi `南 S / 北 U / 東 T / 東南 TG`, note: "Kamar di Selatan, Utara, Timur, atau Tenggara." |
| 6 | Dapur / Kompor | `西 B` | `爐灶宜安西方向東或西北方向東南` | Pills jadi `西→東 / 西北→東南` (atau 2 opsi terpisah), note: "Kompor: duduk Barat menghadap Timur, atau duduk Barat Laut menghadap Tenggara." |

### ❌ HALUSINASI di paragraf — hapus

MD paragraf saat ini berisi:
> "Hindari kamar tidur di sektor Barat Daya yang melambangkan stagnasi."

Foto **tidak menyebut** larangan kamar tidur Barat Daya. **Hapus kalimat ini**.

### ✅ Yang sudah benar (jangan diubah)

- Trigram pribadi 震 ✓
- "Rumah duduk Utara menghadap Selatan, atau duduk Selatan menghadap Utara" ✓ (verbatim foto: 宅宜坐北向南或坐南向北大吉)

---

## ZONE LIST FOTO LENGKAP (referensi untuk template 6 zona)

Foto sebut 7 entry total:
1. **宅** (orientasi rumah keseluruhan) — 坐北向南 atau 坐南向北
2. **門路** (pintu) — 南、北、東南
3. **爐灶** (kompor) — 西方向東 / 西北方向東南
4. **房間** (kamar) — 南、北、東、東南
5. **床位** (ranjang) — 東、東南、南、北 ← MD belum punya entry ini
6. **神位** (altar) — 南 atau 北、東 + 本年大利方
7. **坑廁** (toilet) — 東北、西北、西、西南

Kalau template MD butuh persis 6 zona, kandidat eksklusi adalah **宅** (karena sudah masuk paragraf orientasi rumah). 6 zona final:
1. Pintu (門路)
2. Kompor (爐灶)
3. Kamar (房間)
4. Ranjang (床位) ← baru, ganti slot Ruang Kerja
5. Altar (神位)
6. Toilet (坑廁)

---

## CHECKLIST EKSEKUSI

- [ ] Aku baca foto `06.17.05` (original atau prepped) sendiri, hasil OCR-ku cocok dengan teks verbatim di atas (atau aku flag perbedaan).
- [ ] Aku setuju 3 hard mismatch (kamar mandi/altar/ruang kerja).
- [ ] Aku setuju 3 incomplete perlu dilengkapi.
- [ ] Aku setuju kalimat "Hindari kamar tidur di Barat Daya" halusinasi → hapus.
- [ ] Aku update MD `lixiangfa.md` section `### Yang Zhai`.
- [ ] Aku append catatan di `## CATATAN`.
- [ ] Aku jalankan `python build_pdf.py lixiangfa` dan verifikasi PDF page Yang Zhai tampil benar.
- [ ] Aku lapor ke user: ringkasan diff sebelum/sesudah + path PDF baru.

Kalau ada **disagreement** dengan finding manapun, STOP, jangan fix, lapor user dengan quote foto verbatim yang kau baca.
