# V4.5 Phase 2 — Audit Notes (running)

> Catatan perubahan yang akan dieksekusi BATCH setelah audit semua page selesai.
> Update MD prompt + parse_md.py + template anchors + build_pdf.py engine wiring.

---

## GLOBAL — Footer Caption

**Hapus dari SEMUA halaman** kecuali **page_03_intro** (sisakan footer caption di sini saja).
- Tindakan: hapus `<div class="footer-caption">...</div>` di template 22 halaman
- Page 3 (Intro) tetap tampilkan footer caption Chelsey (dari MD dayun_footer)

---

## Page 9 — Pandangan Keluarga

**Keep**: Subject bar, Footer caption (sudah dari MD).

**Hapus dari template** (tidak penting):
- Headline quote 執行者 (top "Eksekutor handal yang bukan pemegang kekuasaan...")
- Bottom strip 提示 (bawah "Saran: di umur 60-an...")

**MD-driven (4 kartu family) — KRITIS**:
Section MD `### Keluarga & Pasangan` perlu split jadi 4 sub-block:
- `pasangan`: { vibe (2-3 kata, mis "Cerdas · Suportif"), headline (1 kalimat ringkas, max 12 kata), body (50-70 kata) }
- `anak`: { vibe, headline, body }
- `saudari`: { vibe, headline, body }
- `kepemimpinan`: { vibe, headline, body }

Confidence rendah → null per sub-block (engine tidak punya fallback bermakna untuk family — null = kosongkan kartu / placeholder netral).

Engine: anchor `<!-- TAFSIR:family_pasangan -->` x4 di template, inject per slot.

---

## Page 16 — 紫微斗數 Zi Wei (12 Palace Grid)

**DONE engine fix**:
- Palace rotation berdasarkan ming_gong (CCW) — sudah diimplement di render.py
- Stars + age di-hide via CSS (C-minimal: nama palace + branch + shio saja)

**Hapus dari template**:
- Footer caption (global rule)

---

## Page 17 — Palace Detail 1 (命宮 / 兄弟 / 夫妻 / 子女)

**Keep**: Subject bar, layout 4 cards.

**Hapus dari template**:
- Footer caption (global rule)

**MD-driven** (4 palace × 2 sub-fields):
- `palace1_mingmong`: { star (1-2 hanzi), insight (50-70 kata), action (1 baris max 18 kata) }
- `palace1_xiongdi`: { star, insight, action }
- `palace1_fuqi`: { star, insight, action }
- `palace1_zinu`: { star, insight, action }
- confidence rendah → null per palace

Engine: anchor 4× di template `<!-- TAFSIR:palace1_mingmong -->` dst.

---

## Page 18 — Palace Detail 2 (財帛 / 疾厄 / 遷移 / 僕役)

Sama treatment dengan page 17.

**MD-driven** (4 palace × 2 sub-fields):
- `palace2_caibo`: { star, insight (50-70 kata), action (max 18 kata) }
- `palace2_jie`: { star, insight, action }
- `palace2_qianyi`: { star, insight, action }
- `palace2_puyi`: { star, insight, action }

**Hapus**: Footer caption.

---

## NEW Page — Bab III Opener (Penutup / Kesimpulan)

**Tambah halaman baru** setelah page 19 (sebelum page_20_kesimpulan):
- File: `templates/page_19b_penutup_opener.html` (atau nama mirip)
- Format: identik dengan page_05_bazi_opener.html dan page_15_ziwei_opener.html
- Konten generic: 結 atau 終 sebagai watermark, "BAGIAN III · Penutup", hero 結語/總結, list 4 page cards (20 Kesimpulan, 21 Sintesis, 22 Glossarium, 23 Disclaimer)
- Update PAGE_ORDER di render.py (insert sebelum page_20)
- Update footer "Halaman X / 23" → "Halaman X / 24" di SEMUA template
- Update TOC di page_02_toc.html: tambah entry untuk halaman baru, geser nomor halaman 20-23 jadi 21-24

---

## Page 1 — Cover

**Status**: paling bersih, semua rumus/MD-driven.

**Fix**:
- Footer "Laporan 23 Halaman · Mei 2026" → auto-update bulan-tahun saat render (engine).

---

## Page 21 — Sintesis & Saran Aksi

**Keep**: Subject bar, top quote (TAFSIR:sintesis sudah MD), timeline mini (rumus + dayun_seasons MD).

**Hapus dari template**:
- Mantra block (hz + pinyin + meaning) — hapus
- Footer caption (global rule)

**Rebuild**:
- syn-attrib subline: "{strength} · {format_hz} · {format_pinyin}" dari **rumus** (engine sudah punya format_pinyin_map)

**MD-driven** (personalisasi):
- 3 trio cards `synthesis_trio`:
  - `kekuatan`: { hanzi (2 hanzi), pinyin, body (40-60 kata) }
  - `tantangan`: { hanzi, pinyin, body }
  - `tindakan`: { hanzi, pinyin, body }
- 5 actions list `synthesis_actions`: list 5 item, tiap item: { title (max 12 kata), context (max 18 kata), tag (mis. "水 · Air") }

confidence rendah → null per item.

Engine task: fix syn-attrib via rumus + hapus mantra + anchor 3+5 di template.

---

## Page 20 — Kesimpulan Bagan

**Keep**: Subject bar, top quote (TAFSIR:kesimpulan sudah MD), 5 fase life-map (rumus from da_yun), bridge sentence (hapus = ok per user).

**Hapus dari template**:
- Number besar (Umur 64 LinRuYi) — replace dengan rumus age dari data
- Bridge sentence (point #6) — hapus
- Footer caption (global rule)

**Rebuild dari rumus** (6 stat cards — semua data engine sudah ada):
- Card 1 Penguasa Hari: hanzi DM (rumus), strength (rumus dari wuxing %), title "el_id polarity_id strength" (rumus), desc dari wuxing % real (rumus)
- Card 2 Format: hanzi format (rumus), title pinyin+label (rumus dari format_pinyin_map), desc general per format (rumus)
- Card 3 Yong Shen: hanzi yong (rumus), title "el1 & el2 — Penopang+Pengarah" (rumus), desc industri/aspek per yong (rumus general)
- Card 4 Da Yun: current cycle (rumus dari da_yun.cycles[current_index]), title "Fase {ten_god_id} ({age})" (rumus), desc per ten god (rumus)
- Card 5 Da Xian: current palace from age (rumus dari da_xian compute — perlu integrate Zi Wei age-palace mapping)
- Card 6 Kompatibilitas: cocok/hindari (rumus marriage native-derive), trigram (rumus yang_zhai)

Engine task: generate 6 stat cards full HTML dari subject.json di apply_blocks page_20.

---

## Page 19 — Palace Detail 3 (官祿 / 田宅 / 福德 / 父母)

Sama treatment dengan page 17/18.

**MD-driven** (4 palace × 2 sub-fields):
- `palace3_guanlu`: { star, insight (50-70 kata), action (max 18 kata) }
- `palace3_tianzhai`: { star, insight, action }
- `palace3_fude`: { star, insight, action }
- `palace3_fumu`: { star, insight, action }

**Hapus**: Footer caption.

---

## Page 14 — 大運 Da Yun (Peta Hidup)

**Keep**: Subject bar, 10-cycle grid (rumus engine), spotlight headline+bullets (MD dayun_spotlight), 5 seasons (MD dayun_seasons).

**Hapus dari template**:
- 3 tag pills (sp-tags: ten god / tone / combo) — hapus
- Footer caption (global rule)

---

## Page 13 — 陽宅 Feng Shui Hunian

**Keep**: Subject bar, trigram pribadi panel (rumus), trigram description (TAFSIR:yangzhai sudah MD), compass diagram (rumus engine compute 8 zona).

**Hapus dari template**:
- Footer caption (global rule)

**MD-driven**:
- 6 zone arah hoki (kamar tidur / dapur / pintu utama / kamar mandi / dll), tiap zone:
  - `yangzhai_zones`: list 6 item, tiap item: { label (mis. "Kamar Tidur"), headline (✓Optimal/⚠Warn/dll), pills (1-2 arah Hanzi+Indo), note (1 kalimat penjelasan max 18 kata) }
  - confidence rendah → null per zone (engine kosongkan)

---

## Page 12 — 事業 Karir & Profesi

**Keep**: Subject bar, insight body (TAFSIR:career sudah MD).

**Hapus dari template**:
- Bottom advice partner (paragraf bawah list industri)
- Footer caption (global rule)
- Insight body line-clamp + font kecilkan ke 7.5pt — DONE

**MD-driven**:
- Insight tags 4 elemen mendukung/hindari (水/木 ALIRAN-PERTUMBUHAN, 金/土 STATIS-BERAT):
  - `career_tags`: { fav: [{hz, label}, {hz, label}], unfav: [{hz, label}, {hz, label}] }
  - confidence rendah → fallback ke yong_shen + ji_shen dari DATA (sudah ada di engine)
- Industri list (ubah dari 6 jadi **5**, "yang paling searah aja"):
  - `career_industri`: list 5 item, tiap item: { nama (mis. "Pendidikan & Riset"), unsur (1 hanzi), alasan (1 kalimat 12-18 kata) }
  - confidence rendah → null (kosongkan slot atau placeholder netral)

Template: ubah grid industri dari 6 baris jadi 5.

---

## Page 11 — 財富 Rezeki

**Keep**: Subject bar, header big quote (TAFSIR:caifu sudah MD).

**Hapus dari template**:
- Number besar 175% (Jumlah Rezeki) — hapus
- Footer caption (global rule)

**MD-driven**:
- 2 kartu rezeki (正財 Rezeki Tetap / 偏財 Rezeki Tak Terduga + persentase + body):
  - `caifu_zheng`: { label, percent (mis. 60%), body (40-60 kata) }
  - `caifu_pian`: { label, percent (mis. 40%), body (40-60 kata) }
  - confidence rendah → null

**MD-driven**: Aturan Emas Mengelola Rezeki — **4 poin** (bukan 5):
- `caifu_rules`: list 4 item, tiap item: { title (1 baris ringkas, max 12 kata), context (1 kalimat penjelasan, max 25 kata), tone ("tip" hijau atau "warn" merah) }
- confidence rendah → null

Template: ubah dari 5 baris jadi 4 baris.

---

## Page 10 — Shen Sha (Bintang Pelengkap)

**Keep**: Subject bar, hero body paragraph (TAFSIR:shensha — sudah MD).

**Hapus dari template**:
- 6 cards kanan (華蓋/劫煞/紅鸞/天德/dll dengan "dormant") — tidak penting
- Footer caption (global rule)

**MD-driven (KRITIS)**:
- Hero block kiri (bintang dominan):
  - `dominant_star_hz` (1-2 hanzi, mis. 驛馬 / 桃花 / 天乙 / 文昌)
  - `dominant_star_pinyin` (mis. Yì Mǎ)
  - `dominant_star_label_id` (mis. "Bintang Perpindahan")
  - `dominant_star_active_label` (mis. "AKTIF SEKARANG" atau "DORMANT")
  - confidence rendah → null (engine kosongkan blok atau placeholder netral)
- Insight strip 建議 (bawah, prosa saran):
  - Add field `shensha_strip` (1-2 kalimat, max 30 kata)
  - confidence rendah → null

Engine: anchor `<!-- TAFSIR:shensha_dominant -->` (untuk hero kiri label) + `<!-- TAFSIR:shensha_strip -->` di template.

---
