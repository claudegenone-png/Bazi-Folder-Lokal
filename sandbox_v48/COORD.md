# V4.8 — Multi-Agent Coordination Board

**Project:** `sandbox_v48/` (mirror `C:\temp\v48\`)
**Goal:** Per-page polish supaya semua halaman cantik, konsisten, dan adaptif untuk MD struktur beda-beda.
**Test MD utama:** `C:/Users/sukam/Downloads/Train/2/laporan_astrologi_li_yuanxiang.md` (paling dense, 24+ bab)

---

## Coordination Protocol

1. **Sebelum edit page**: ubah `STATUS` di tabel di bawah → `🔒 IN PROGRESS · {agent-name}`
2. **Setelah selesai polish**: ubah → `✅ DONE · {agent-name}` + isi commit-note
3. **Jangan pernah edit page yang `🔒 IN PROGRESS · {other-agent}`** — pilih page lain yang `⏸ PENDING`
4. **Selalu sync ke OneDrive** setelah edit: `Copy-Item -Force C:\temp\v48\templates\{file}.py c:\Users\sukam\OneDrive\Documents\Ramalan\sandbox_v48\templates\{file}.py`
5. **Test setiap edit**: `cd C:\temp\v48 && python v48.py "C:/Users/sukam/Downloads/Train/2/laporan_astrologi_li_yuanxiang.md"`
6. **Wajib ikut aturan memori `feedback_design_universal.md`**:
   - Hanzi wajib + Indo gloss
   - Dilarang plain text (semua dalam kartu/box)
   - Dilarang konten ke-clip / ke-cut
   - 70% visualisasi / 30% teks
   - Dilarang page-break sebelum halaman penuh

---

## Agent Direction Assignment

| Agent | Direction | Domain |
|-------|-----------|--------|
| **Agent 1** (top-down) | Cover → TOC → Pengantar → BaZi → Karakter → Generic sections (Aspek Kehidupan) → ... | Halaman atas + tengah |
| **Agent 2** (bottom-up) | Disclaimer → Kesimpulan → Tahunan → Hikmat Klasik → Peruntungan → ... | Halaman bawah + tengah |

**Meet in middle:** ketika kedua agent meet di Aspek Kehidupan generic section, koordinasi via COORD.md.

---

## Page Status Board

| # | Template File | Page Topic | Status | Last Polished By | Notes |
|---|---|---|---|---|---|
| 1 | `templates/cover.py` | Cover | ✅ DONE | Agent 1 | V4.6 hero + shio SVG + 7-row info panel |
| 2 | `templates/toc.py` | Daftar Isi | ✅ DONE | Agent 1 | 1-column drop-down, sorted by page, Roman urut |
| 3 | `templates/pengantar.py` | Pengantar & Cara Membaca | ✅ DONE | Agent 1 | Port V4.6 visual exactly: hero red gradient + 3 method cards (BaZi/ZiWei highlighted/FengShui) + 2 section "Cara Membaca" (4 step cards) + "Skala Persentase" (3 demo bars) + closing seal. Universal hardcoded content, sama untuk semua subjek. |
| 4 | `templates/bazi_page.py` | Empat Pilar BaZi | ✅ DONE · Agent 1 | Agent 1 | Port V4.6: lead callout + 4-pilar grid (element chip + ten god + DM badge) + Wu Xing distribution chart (5 vertical bars color-coded by yong/xi/ji) + 5 Dewa Elemen cards (Yong=gold/Xi=green/Ji=warn). Extractor compute wuxing_count from pilar gan+zhi. |
| 5 | `templates/karakter_page.py` | Karakter & Kepribadian | ✅ DONE · Agent 1 | Agent 1 | Layout: red interpretasi card top + section heading "Lapisan-Lapisan Kepribadian" + numbered Lapisan cards (label + body + sub-bullets). EXTRACTOR juga di-improve (Agent 1 extension): tambah inline-label patterns (Lin Ruyi style `**Lapisan Pertama (X):** body` inline), tambah "section header" detection (Interpretasi/Lima Pola/dst → ke intro mode bukan card), skip standalone **bold** meta lines. Hasil: 3 Lapisan (Lin Ruyi), 3 Lapisan (Li Yuanxiang), 5 Pola (Lin Wen Han). |
| 6 | `templates/generic_section.py` | Generic (semua Aspek Kehidupan + topik UNKNOWN) | ✅ DONE · Agent 1 | Agent 1+2 | Agent 2 udah buat visual-led layout (drop-cap, mood bullets, ratings, tables, callouts). Agent 1 tambah `_extract_interpretasi` 3-strategy: subject-specific blockquote (💡 dst) → ### Interpretasi sub → first non-Hanzi paragraph. Render red gradient `gs-interp` card di top kalau extracted. Filter ●/◎/Hanzi-dominant lines. Test Li Yuanxiang: 13 pages dapat interpretasi card. |
| 7 | `templates/tahunan_page.py` | Ramalan Tahunan | ⏸ PENDING | — | Year cards 3/page |
| 8 | `templates/ringkasan_page.py` | Kesimpulan & Saran | ⏸ PENDING | — | Last bab |
| 9 | (belum ada) | Disclaimer / Penutup | ⏸ TODO-CREATE | — | Perlu dibuat (saat ini tidak ada) |
| 10 | `templates/ziwei_page.py` | Peta Bintang Zi Wei | ✅ DONE · Agent 1 | Agent 1 | New: extractor `extract_ziwei` + template. Layout: red interpretasi top + Data Inti panel (2-col KV) + 4 Transformasi cards (祿/權/科/忌 color-coded) + 12 Palace grid (4×3 cards, filled/empty graceful). Adaptive: parse subs `### Data Inti / ### Empat Transformasi / ### Struktur 12 Istana`. Test 3 MD: Lin Ruyi (12 palaces ✓), Li Yuanxiang (data inti+trans ✓), Lin Wen Han (trans+interp ✓). |
| 11 | `templates/istana_detail_page.py` | Detail Per Istana (MD1 collection + MD2/MD3 synthesized) | ✅ DONE · Agent 1 | Agent 1 | Custom template + extractor. Strategy A (MD1): collection H2 dengan 6+ sub-istana. Strategy B (MD2/MD3): synthesize dari 4+ individual istana H2 BAB. Output: card stack 6 per page. Per card: number + icon + nama (strip "Istana"+Hanzi) + bintang chip + ganzhi + interpretasi (paragraf+bullets) + saran/catatan/peringatan callout (mood-coded). Saran patterns: blockquote (`> 💼 **Saran:** body`), inline (`**Saran:** body`), standalone (`**Peringatan Penting:**` + bullets). Keywords: Saran/Catatan/Tips/Note/Pesan/Rekomendasi/Peringatan/Pengingat/Anjuran. |
| 12 | `templates/kecocokan_shio_page.py` | Kecocokan Shio Pasangan | 🤝 HANDED-OFF to Agent 2 | Agent 1 (drafted) | Agent 1 sudah draft scaffold (canonical KecocokanShio+ShioMatch, extractor 3-pola adaptive, template 12-shio grid+breakdown). UNWIRED dari v48.py — Agent 2 silakan review/polish/wire kembali. Files: extractors/kecocokan_shio.py, templates/kecocokan_shio_page.py |
| 13 | `templates/fengshui_page.py` | Feng Shui Rumah | ✅ DONE · Agent 1 | Agent 1 | New: canonical FengShuiRumah+FengShuiElement, extractor parse tabel + trigram + saran, template visual: red interpretasi top + Trigram hero card (Hanzi 36pt + Indo + meaning) + 8-direction compass SVG inline + element stack (icon + aspek + arah chips). 3 MD test: Lin Ruyi 坎卦+7 elements, Li Yuanxiang 坤卦+7, Lin Wen Han 7 elements (no trigram). |

---

## File Editing Rules

- **EDIT di** `C:\temp\v48\` (Write tool friendly, no EBADF)
- **SYNC ke** `c:\Users\sukam\OneDrive\Documents\Ramalan\sandbox_v48\` setelah edit
- **OUTPUT HTML** ke `C:\Users\sukam\OneDrive\Documents\Ramalan\#result\{date}\_test_v48\full_{Name}.html`
- **JANGAN edit** files di OneDrive secara langsung (Write tool kadang EBADF)

## Files yang BOLEH dibagi-edit antar agent (jangan overlap timing)

| File | Owner default | Catatan |
|---|---|---|
| `templates/*.py` | per page above | satu agent = satu file in-progress |
| `templates/page_shell.py` | shared (read-only by default) | edit hati-hati — affects semua page |
| `templates/primitives.py` | shared (read-only by default) | tambah primitif baru OK, jangan ubah existing API |
| `design_system/tokens.css` | shared (read-only by default) | tambah token baru OK, jangan ubah existing var name |
| `lookups/*.py` | append-only by both | tambah Hanzi baru OK, jangan ubah existing entries |
| `extractors/*.py` | jangan diubah Agent 2 (Agent 1 punya context full extractor) | beritahu Agent 1 kalau butuh field baru |
| `canonical_model.py` | Agent 1 only (perubahan schema = breaking) | request via COORD.md |
| `v48.py` | Agent 1 only (entry point, hindari conflict) | |

## Append-only sections

### Lookup additions log
(Tambahkan baris setiap menambah Hanzi baru ke `lookups/hanzi_universal.py`)

- (kosong)

### Primitive additions log
(Tambahkan baris setiap menambah primitif baru ke `templates/primitives.py`)

- (kosong)

### Design token additions log
(Tambahkan baris setiap menambah CSS variable baru ke `design_system/tokens.css`)

- (kosong)
