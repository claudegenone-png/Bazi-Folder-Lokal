"""Glossary 2-page hardcoded V4.8 (port from V4.5).

Page 1 — Dasar BaZi: 八字 基礎 + 五行 元素 + 十神 (10 dewa)
Page 2 — Zi Wei + Feng Shui: 紫微 主星 + 四化 + 十二宮 + 神煞 + 其他

Adaptive untuk semua subjek (hardcoded universal — tidak per-subject).
"""
from templates.page_shell import page_shell


def _row(term_hz, py, meaning):
    return (f'<div class="glo-row"><div class="glo-term">{term_hz}'
            f'<span class="py">{py}</span></div>'
            f'<div class="glo-meaning">{meaning}</div></div>')


def _section(hz, indo, count_label, rows_html, cols=2):
    cls = "glo-list" + (" cols-3" if cols == 3 else "")
    return f'''<div class="glo-section">
  <div class="glo-section-head">
    <span class="glo-section-hz">{hz}</span>
    <span class="glo-section-id">{indo}</span>
    <span class="glo-section-count">{count_label}</span>
  </div>
  <div class="{cls}">
    {rows_html}
  </div>
</div>'''


def _page1_body():
    # Dasar BaZi (10 istilah)
    dasar = "\n".join([
        _row("八字", "Bā Zì", "“Delapan Karakter” = sistem 4 pilar"),
        _row("四柱", "Sì Zhù", "“Empat Pilar” = Tahun · Bulan · Hari · Jam"),
        _row("日主", "Rì Zhǔ", "<strong>Penguasa Hari</strong> = Stem dari pilar Hari, inti diri"),
        _row("命主", "Mìng Zhǔ", "<strong>Penguasa Hidup</strong> = bintang utama nasib"),
        _row("身主", "Shēn Zhǔ", "<strong>Penguasa Tubuh</strong> = bintang utama fisik"),
        _row("天干", "Tiān Gān", "10 Batang Langit (甲乙丙丁戊己庚辛壬癸)"),
        _row("地支", "Dì Zhī", "12 Cabang Bumi = 12 shio (子丑寅卯…)"),
        _row("格局", "Gé Jú", "“Format” = pola dasar kepribadian"),
        _row("十神", "Shí Shén", "“10 Dewa” = relasi pilar terhadap Penguasa Hari"),
        _row("大運", "Dà Yùn", "<strong>Great Cycles</strong> = fase 10 tahunan"),
    ])
    # Wu Xing (8)
    wuxing = "\n".join([
        _row("五行", "Wǔ Xíng", "5 Elemen = siklus generatif/destruktif energi"),
        _row("金", "Jīn", "<strong>Logam</strong> = ketegasan, eksekusi, ketajaman"),
        _row("木", "Mù", "<strong>Kayu</strong> = pertumbuhan, fleksibilitas, edukasi"),
        _row("水", "Shuǐ", "<strong>Air</strong> = aliran, refleksi, intelek"),
        _row("火", "Huǒ", "<strong>Api</strong> = semangat, transformasi, ekspresi"),
        _row("土", "Tǔ", "<strong>Tanah</strong> = stabilitas, akumulasi, pondasi"),
        _row("喜用神", "Xǐ Yòng Shén", "Elemen <strong>mendukung</strong> Anda"),
        _row("忌神", "Jì Shén", "Elemen <strong>tidak mendukung</strong> Anda"),
    ])
    # 10 Dewa lengkap (10 + 喜用)
    dewa = "\n".join([
        _row("比肩", "Bǐ Jiān", "<strong>Saudara Sebanding</strong> = kemandirian, peer"),
        _row("劫財", "Jié Cái", "<strong>Saudara Pesaing</strong> = kompetisi, persahabatan"),
        _row("食神", "Shí Shén", "<strong>Dewa Makanan</strong> = kreativitas, produktivitas"),
        _row("傷官", "Shāng Guān", "<strong>Pejabat Cedera</strong> = bakat, ekspresi bebas"),
        _row("正財", "Zhèng Cái", "<strong>Rezeki Tetap</strong> = gaji, aset stabil"),
        _row("偏財", "Piān Cái", "<strong>Rezeki Sampingan</strong> = bisnis, peluang"),
        _row("正官", "Zhèng Guān", "<strong>Pejabat Resmi</strong> = karir formal, status"),
        _row("七殺", "Qī Shā", "<strong>Tujuh Pembunuh</strong> = tantangan, terobosan"),
        _row("正印", "Zhèng Yìn", "<strong>Stempel Resmi</strong> = perlindungan, ilmu"),
        _row("偏印", "Piān Yìn", "<strong>Stempel Sampingan</strong> = intuisi, mistis"),
    ])
    parts = [
        '<div class="glo-frame">',
        '''<div class="glo-eyebrow">
  <div><span class="label">辭 典</span><span class="id">Cí Diǎn — Daftar Istilah · Halaman 1</span></div>
  <div class="meta">3 KATEGORI · 28 ISTILAH</div>
</div>''',
        _section("八字 基礎", "Dasar BaZi", "10 istilah", dasar, cols=2),
        _section("五行 元素", "Lima Elemen", "8 istilah", wuxing, cols=2),
        _section("十 神", "Sepuluh Dewa (Ten Gods)", "10 istilah", dewa, cols=2),
        '</div>',
    ]
    return "\n".join(parts)


def _page2_body():
    # Zi Wei stars (8)
    ziwei = "\n".join([
        _row("紫微", "Zǐ Wēi", "<strong>Bintang Kaisar</strong> = kepemimpinan, prestige"),
        _row("天府", "Tiān Fǔ", "<strong>Lumbung Stabilitas</strong> = kekayaan, tenang"),
        _row("廉貞", "Lián Zhēn", "<strong>Integritas</strong> = disiplin, karir"),
        _row("天梁", "Tiān Liáng", "<strong>Pelindung</strong> = kebijaksanaan, mentor"),
        _row("天機", "Tiān Jī", "<strong>Bintang Strategi</strong> = kecerdasan, analisis"),
        _row("巨門", "Jù Mén", "<strong>Pintu Besar</strong> = komunikasi, argumentasi"),
        _row("七殺", "Qī Shā", "<strong>Tujuh Pembunuh</strong> = pemurnian, transformasi"),
        _row("貪狼", "Tān Láng", "<strong>Serigala Tamak</strong> = daya tarik, hasrat"),
        _row("武曲", "Wǔ Qū", "<strong>Bintang Logam</strong> = kekayaan, ketegasan"),
        _row("太陰", "Tài Yīn", "<strong>Bulan</strong> = kelembutan, intuisi feminin"),
    ])
    # 4 Hua + 8 Trigram
    sihua = "\n".join([
        _row("化祿", "Huà Lù", "<strong>Berkah</strong> = rezeki & peluang"),
        _row("化權", "Huà Quán", "<strong>Kuasa</strong> = otoritas & pengaruh"),
        _row("化科", "Huà Kē", "<strong>Reputasi</strong> = nama baik & ilmu"),
        _row("化忌", "Huà Jì", "<strong>Tantangan</strong> = pelajaran & ujian"),
        _row("八卦", "Bā Guà", "8 Trigram (☰乾 ☷坤 ☵坎 ☲離 ☳震 ☴巽 ☶艮 ☱兌)"),
        _row("陽宅", "Yáng Zhái", "Feng Shui hunian = energi rumah"),
    ])
    # 12 Istana
    istana = "\n".join([
        _row("命宮", "Mìng Gōng", "Diri / Kepribadian inti"),
        _row("兄弟", "Xiōng Dì", "Saudara / Teman akrab"),
        _row("夫妻", "Fū Qī", "Pasangan / Pernikahan"),
        _row("子女", "Zǐ Nǚ", "Anak / Kreativitas"),
        _row("財帛", "Cái Bó", "Rezeki / Keuangan"),
        _row("疾厄", "Jí È", "Kesehatan / Tubuh"),
        _row("遷移", "Qiān Yí", "Perpindahan / Peluang luar"),
        _row("僕役", "Pú Yì", "Bawahan / Jaringan kerja"),
        _row("官祿", "Guān Lù", "Karir / Profesi"),
        _row("田宅", "Tián Zhái", "Properti / Aset tetap"),
        _row("福德", "Fú Dé", "Berkah / Kebahagiaan batin"),
        _row("父母", "Fù Mǔ", "Orang tua / Atasan"),
    ])
    # Shensha + lain
    shensha = "\n".join([
        _row("神煞", "Shén Shà", "Bintang nasib pelengkap"),
        _row("太歲", "Tài Suì", "Penguasa tahun = energi tahunan"),
        _row("驛馬", "Yì Mǎ", "“Kuda Pos” = gerak/perjalanan"),
        _row("桃花", "Táo Huā", "“Bunga Persik” = pesona, asmara"),
        _row("華蓋", "Huá Gài", "“Kanopi Megah” = bakat seni & spiritual"),
        _row("龍德", "Lóng Dé", "Bintang naga = perlindungan kebajikan"),
        _row("羊刃", "Yáng Rèn", "“Pisau Domba” = kekuatan tajam"),
        _row("文昌", "Wén Chāng", "Bintang akademik = ilmu & ujian"),
        _row("文曲", "Wén Qū", "Bintang seni & komunikasi"),
        _row("流年", "Liú Nián", "Tahun berjalan = energi tahunan"),
    ])
    parts = [
        '<div class="glo-frame">',
        '''<div class="glo-eyebrow">
  <div><span class="label">辭 典</span><span class="id">Cí Diǎn — Daftar Istilah · Halaman 2</span></div>
  <div class="meta">4 KATEGORI · 38 ISTILAH</div>
</div>''',
        _section("紫微 主星", "Bintang Utama Zi Wei", "10 istilah", ziwei, cols=2),
        _section("四化 + 八卦", "Empat Transformasi & Trigram", "6 istilah", sihua, cols=2),
        _section("十二宮", "Dua Belas Istana Hidup", "12 istilah", istana, cols=3),
        _section("神煞 + 流年", "Bintang Nasib & Tahunan", "10 istilah", shensha, cols=2),
        '</div>',
    ]
    return "\n".join(parts)


def render_glossary_pages(start_pn: int, subject_name: str = ""):
    """Returns ([page_html_1, page_html_2], next_pn)."""
    p1 = page_shell(
        start_pn, "Daftar Istilah", "辭 典 · I",
        "PENUTUP · 結 語",
        _page1_body(),
        subject_name,
        footer_l="Glossary — Dasar BaZi & Lima Elemen",
    )
    p2 = page_shell(
        start_pn + 1, "Daftar Istilah", "辭 典 · II",
        "PENUTUP · 結 語",
        _page2_body(),
        subject_name,
        footer_l="Glossary — Zi Wei, 12 Istana & Bintang Nasib",
    )
    return [p1, p2], start_pn + 2


GLOSSARY_PAGE_CSS = """
/* === GLOSSARY PAGE V4.8 === */
.glo-frame {
  background: var(--color-paper);
  border: 0.3mm solid var(--color-gold-soft);
  border-radius: var(--r-md);
  padding: 4mm 5mm;
  display: flex; flex-direction: column;
  gap: 3mm;
  height: 100%;
  overflow: hidden;
}
.glo-eyebrow {
  display: flex; justify-content: space-between; align-items: baseline;
  border-bottom: 0.3mm solid var(--color-gold-soft); padding-bottom: 1.8mm;
  flex-shrink: 0;
}
.glo-eyebrow .label {
  font-family: var(--font-serif-tc); font-size: 13pt;
  color: var(--color-red); letter-spacing: 4px; font-weight: 700;
}
.glo-eyebrow .id {
  font-family: var(--font-display); font-size: 9pt;
  font-style: italic; color: var(--color-muted); margin-left: 4mm;
}
.glo-eyebrow .meta {
  font-size: 6.5pt; color: var(--color-muted);
  letter-spacing: 1.5px; text-transform: uppercase; font-weight: 600;
}

.glo-section {
  display: flex; flex-direction: column; gap: 1.5mm;
  break-inside: avoid;
}
.glo-section-head {
  display: flex; align-items: baseline; gap: 3mm;
  background: linear-gradient(90deg, var(--color-gold-tint), transparent);
  border-left: 1mm solid var(--color-gold);
  border-radius: 0 1mm 1mm 0;
  padding: 1.4mm 3mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.glo-section-hz {
  font-family: var(--font-serif-tc); font-size: 11pt;
  color: var(--color-red); font-weight: 700; letter-spacing: 2px;
  line-height: 1;
}
.glo-section-id {
  font-family: var(--font-display); font-size: 8.5pt;
  color: var(--color-ink); font-weight: 600; font-style: italic;
}
.glo-section-count {
  font-family: var(--font-body); font-size: 6pt;
  color: var(--color-muted); letter-spacing: 1.5px;
  text-transform: uppercase; margin-left: auto;
}

.glo-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.8mm 5mm;
  padding-left: 4mm;
}
.glo-list.cols-3 { grid-template-columns: repeat(3, 1fr); }

.glo-row {
  display: grid; grid-template-columns: 16mm 1fr;
  gap: 2mm; align-items: baseline;
  padding: 0.6mm 0;
  border-bottom: 0.12mm dotted var(--color-gold-soft);
  font-size: 7pt; line-height: 1.25;
  overflow: hidden; min-width: 0;
}
.glo-term {
  font-family: var(--font-serif-tc); font-size: 8.5pt;
  color: var(--color-red); font-weight: 700; line-height: 1;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.glo-term .py {
  font-family: var(--font-display); font-size: 5.8pt;
  color: var(--color-muted); font-style: italic;
  display: block; margin-top: 0.3mm;
  font-weight: 500; letter-spacing: 0.3px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.glo-meaning {
  color: var(--color-ink); font-size: 6.8pt; line-height: 1.3;
  overflow: hidden;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.glo-meaning strong { color: var(--color-red); font-weight: 600; }
"""
