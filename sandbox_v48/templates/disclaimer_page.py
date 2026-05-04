"""Disclaimer & Etika — last page V4.8 (port from V4.5).

Layout:
1. Hero card (cream gradient + 告白 seal + tagline)
2. 4-card grid: Dont (red) · Do (green) · Scope (gold) · Legal (gold)
3. Closing red gradient (命由己造 quote + 完 mark)

Universal hardcoded — sama untuk semua subjek.
"""
from templates.page_shell import page_shell


def _body():
    return '''<div class="dis-frame">

  <div class="dis-hero">
    <div class="dh-seal">告白</div>
    <div class="dh-text">
      <div class="dh-eb">Etika &amp; Batasan</div>
      <div class="dh-quote">
        Bagan ini adalah <span class="hz">peta pola</span>, bukan vonis. Pakai sebagai referensi tradisi &amp; <strong>eksplorasi diri</strong> — keputusan tetap di tangan Anda.
      </div>
    </div>
  </div>

  <div class="dis-cards">

    <div class="dc-card dont">
      <div class="dc-eb">不 用 · Yang Tidak Dilakukan</div>
      <div class="dc-title"><span class="dc-hz">禁忌</span><span class="dc-name">Jìn Jì · Larangan Etis</span></div>
      <div class="dc-list">
        <div class="dc-item"><span class="ico">✗</span><span>Tidak ada <strong>prediksi kematian</strong> dalam bentuk apapun</span></div>
        <div class="dc-item"><span class="ico">✗</span><span>Tidak ada kalimat absolut (&ldquo;PASTI akan…&rdquo;, &ldquo;TIDAK MUNGKIN…&rdquo;)</span></div>
        <div class="dc-item"><span class="ico">✗</span><span>Tidak ada <strong>diagnosa medis/hukum</strong> spesifik</span></div>
        <div class="dc-item"><span class="ico">✗</span><span>Tidak ada bahasa menakutkan atau intimidasi</span></div>
      </div>
    </div>

    <div class="dc-card do">
      <div class="dc-eb">必 行 · Yang Dijamin</div>
      <div class="dc-title"><span class="dc-hz">原則</span><span class="dc-name">Yuán Zé · Prinsip Etis</span></div>
      <div class="dc-list">
        <div class="dc-item"><span class="ico">✓</span><span>Bahasa <strong>pemberdayaan</strong>: &ldquo;kecenderungan&rdquo;, &ldquo;trend&rdquo;, &ldquo;potensi&rdquo;</span></div>
        <div class="dc-item"><span class="ico">✓</span><span>Bahasa negatif <strong>dibalik konstruktif</strong>: tantangan dapat diatasi</span></div>
        <div class="dc-item"><span class="ico">✓</span><span>Saran berbasis <strong>data sumber</strong>, bukan opini bebas</span></div>
        <div class="dc-item"><span class="ico">✓</span><span>Pengakuan: <strong>budaya, bukan ilmu pasti</strong></span></div>
      </div>
    </div>

    <div class="dc-card scope">
      <div class="dc-eb">範 圍 · Cakupan</div>
      <div class="dc-title"><span class="dc-hz">範圍</span><span class="dc-name">Fàn Wéi · Scope</span></div>
      <div class="dc-list">
        <div class="dc-item"><span class="ico">◆</span><span>Sumber data: <strong>laporan astrologi</strong> 四柱論命 + 紫微斗數</span></div>
        <div class="dc-item"><span class="ico">◆</span><span>Methodology multi-school: <span class="hz">三命通會</span>, <span class="hz">子平真詮</span>, <span class="hz">滴天髓</span></span></div>
        <div class="dc-item"><span class="ico">◆</span><span>Cakupan: 八字 + 紫微 + 陽宅 (BaZi-based, bukan 八宅)</span></div>
        <div class="dc-item"><span class="ico">◆</span><span>Tidak menambah prediksi <strong>di luar sumber</strong></span></div>
      </div>
    </div>

    <div class="dc-card legal">
      <div class="dc-eb">法 律 · Pernyataan Hukum</div>
      <div class="dc-title"><span class="dc-hz">聲明</span><span class="dc-name">Shēng Míng · Pernyataan</span></div>
      <div class="dc-list">
        <div class="dc-item"><span class="ico">◆</span><span>Bagan ini <strong>tidak menggantikan</strong> keputusan medis profesional</span></div>
        <div class="dc-item"><span class="ico">◆</span><span><strong>Tidak menggantikan</strong> nasihat hukum atau finansial</span></div>
        <div class="dc-item"><span class="ico">◆</span><span>Tidak menjamin akurasi terjemahan istilah klasik (lihat <span class="hz">辭典</span>)</span></div>
        <div class="dc-item"><span class="ico">◆</span><span>Subjek &amp; pembuat tidak bertanggung jawab atas keputusan berdasarkan laporan ini</span></div>
      </div>
    </div>

  </div>

  <div class="dis-close">
    <div class="dc-close-text">
      <div class="dc-close-eb">Penutup</div>
      <div class="dc-close-quote">
        &ldquo;<span class="hz">命由己造，相由心生</span>&rdquo; — Takdir dibentuk oleh diri sendiri; wajah lahir dari hati. Bagan ini cermin pola; <strong>kunci tetap di tangan Anda</strong>.
      </div>
    </div>
    <div class="dc-close-mark">完</div>
  </div>

</div>'''


def render_disclaimer_page(pn: int, subject_name: str = "") -> str:
    return page_shell(
        pn, "Disclaimer & Etika", "告 白",
        "PENUTUP · 結 語",
        _body(),
        subject_name,
        footer_l="Mìng Yóu Jǐ Zào — Xiāng Yóu Xīn Shēng · 福壽財",
    )


DISCLAIMER_PAGE_CSS = """
/* === DISCLAIMER PAGE V4.8 === */
.dis-frame {
  display: grid; grid-template-rows: auto 1fr auto;
  gap: 4mm; height: 100%; overflow: hidden;
}

/* Hero */
.dis-hero {
  background: linear-gradient(135deg, #FFF8E1 0%, #F5EBD0 100%);
  border: 0.5mm solid var(--color-gold);
  border-radius: var(--r-md);
  padding: 5mm 8mm;
  display: grid; grid-template-columns: auto 1fr;
  gap: 6mm; align-items: center;
  overflow: hidden; position: relative;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.dis-hero::before {
  content: '告'; position: absolute;
  bottom: -10mm; right: -2mm;
  font-family: var(--font-serif-tc);
  font-size: 90pt; color: rgba(139,26,26,0.05);
  font-weight: 700; line-height: 1; pointer-events: none;
}
.dh-seal {
  width: 22mm; height: 22mm;
  background: var(--color-red); color: #fff;
  font-family: var(--font-serif-tc); font-size: 16pt; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border-radius: 1.5mm; transform: rotate(-3deg);
  letter-spacing: 1px;
  box-shadow: 0 2mm 4mm rgba(139,26,26,0.3);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.dh-text { min-width: 0; }
.dh-eb {
  font-size: 7pt; color: var(--color-gold-deep);
  letter-spacing: 3px; text-transform: uppercase; font-weight: 700;
}
.dh-quote {
  font-family: var(--font-display); font-size: 13pt;
  color: var(--color-ink); line-height: 1.4; font-style: italic;
  margin-top: 1.5mm; font-weight: 600;
}
.dh-quote .hz {
  font-family: var(--font-serif-tc); color: var(--color-red);
  font-style: normal; font-weight: 700;
}
.dh-quote strong { color: var(--color-red); }

/* Card grid */
.dis-cards {
  display: grid; grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 4mm; overflow: hidden;
}
.dc-card {
  border-radius: var(--r-md); padding: 3mm 4mm;
  display: grid; grid-template-rows: auto auto 1fr;
  gap: 1.2mm; overflow: hidden;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.dc-card.dont  { background: #FFF1F0; border: 0.4mm solid #C44; }
.dc-card.do    { background: #F0F9F2; border: 0.4mm solid #4A8B5F; }
.dc-card.scope { background: var(--color-paper); border: 0.4mm solid var(--color-gold-soft); }
.dc-card.legal { background: var(--color-paper); border: 0.4mm solid var(--color-gold-soft); }

.dc-eb {
  font-size: 7pt; letter-spacing: 2.5px;
  text-transform: uppercase; font-weight: 700;
}
.dc-card.dont  .dc-eb { color: #C44; }
.dc-card.do    .dc-eb { color: #4A8B5F; }
.dc-card.scope .dc-eb { color: var(--color-gold-deep); }
.dc-card.legal .dc-eb { color: var(--color-gold-deep); }

.dc-title {
  display: flex; align-items: baseline; gap: 3mm;
  border-bottom: 0.2mm solid rgba(0,0,0,0.08);
  padding-bottom: 1.5mm;
}
.dc-hz {
  font-family: var(--font-serif-tc); font-size: 18pt;
  font-weight: 700; line-height: 1;
}
.dc-card.dont  .dc-hz { color: #C44; }
.dc-card.do    .dc-hz { color: #4A8B5F; }
.dc-card.scope .dc-hz { color: var(--color-red); }
.dc-card.legal .dc-hz { color: var(--color-red); }

.dc-name {
  font-family: var(--font-display); font-size: 10.5pt;
  color: var(--color-ink); font-style: italic; font-weight: 600;
}

.dc-list {
  font-size: 7pt; line-height: 1.35; color: var(--color-ink);
  display: flex; flex-direction: column; gap: 1.2mm;
}
.dc-item {
  display: grid; grid-template-columns: 4mm 1fr;
  gap: 2mm;
}
.dc-item .ico { font-weight: 700; }
.dc-card.dont  .dc-item .ico { color: #C44; }
.dc-card.do    .dc-item .ico { color: #4A8B5F; }
.dc-card.scope .dc-item .ico { color: var(--color-gold-deep); }
.dc-card.legal .dc-item .ico { color: var(--color-gold-deep); }
.dc-item strong { color: var(--color-red); }
.dc-item .hz { font-family: var(--font-serif-tc); color: var(--color-red); font-weight: 600; }

/* Closing red banner */
.dis-close {
  background: linear-gradient(135deg, #8B1A1A 0%, #6E1414 100%);
  color: #fff; border-radius: var(--r-md);
  padding: 5mm 8mm;
  display: grid; grid-template-columns: 1fr auto;
  gap: 6mm; align-items: center;
  overflow: hidden; position: relative;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.dc-close-text { min-width: 0; overflow: hidden; }
.dc-close-eb {
  font-size: 6.5pt; color: rgba(245,235,208,0.7);
  letter-spacing: 3px; text-transform: uppercase;
  font-weight: 600; margin-bottom: 1mm;
}
.dc-close-quote {
  font-family: var(--font-display); font-size: 11.5pt;
  color: #F5EBD0; line-height: 1.45; font-style: italic;
}
.dc-close-quote .hz {
  font-family: var(--font-serif-tc); color: #fff;
  font-style: normal; font-weight: 700;
}
.dc-close-quote strong { color: #fff; font-weight: 700; }
.dc-close-mark {
  font-family: var(--font-serif-tc); font-size: 30pt;
  color: #F5EBD0; font-weight: 700; line-height: 1;
  letter-spacing: 4px;
  text-shadow: 0 1mm 3mm rgba(0,0,0,0.2);
}
"""
