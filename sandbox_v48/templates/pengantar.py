"""Pengantar page V4.8 — port V4.6 hardcoded content (universal, same for everyone).

Content sections (same for all subjects):
1. pg-hero: 前 huge mark + Welcome title + intro
2. pg-method-grid: 3 cards explaining BaZi / ZiWei / FengShui systems
3. Section "1. Cara Membaca Laporan" + 4 step cards (01-04)
4. Section "2. Skala Persentase Bawaan" + 3 demo bars (high/mid/low)
5. pg-closing: 命 seal + closing message

Hardcoded body — no MD-derived content.
"""
from templates.page_shell import page_shell


PENGANTAR_BODY = """<div class="pg-hero">
  <div class="pg-hero-mark">前</div>
  <div class="pg-hero-text">
    <div class="pg-hero-title">Selamat Datang</div>
    <div class="pg-hero-sub">Laporan ini adalah <strong>peta</strong> bawaan kelahiran Anda — bukan vonis takdir.
    Setiap bab membahas karakter, karir, keuangan, hubungan, kesehatan, dan masa depan, plus rangkuman saran praktis.</div>
  </div>
</div>

<div class="pg-method-grid">
  <div class="pg-method-card">
    <div class="pg-method-hz">八字</div>
    <div class="pg-method-py">Bā Zì</div>
    <div class="pg-method-id">Empat Pilar Kelahiran</div>
    <div class="pg-method-desc">Sistem berdasarkan <strong>Tahun · Bulan · Hari · Jam</strong> lahir — fondasi karakter, keuangan, kesehatan, &amp; relasi.</div>
  </div>
  <div class="pg-method-card highlight">
    <div class="pg-method-hz">紫微</div>
    <div class="pg-method-py">Zǐ Wēi Dǒu Shù</div>
    <div class="pg-method-id">12 Istana Hidup</div>
    <div class="pg-method-desc">Memetakan <strong>12 istana</strong> — pasangan, anak, properti, karir — masing-masing dihuni bintang arketipe.</div>
  </div>
  <div class="pg-method-card">
    <div class="pg-method-hz">陽宅</div>
    <div class="pg-method-py">Yáng Zhái</div>
    <div class="pg-method-id">Feng Shui Rumah</div>
    <div class="pg-method-desc">Tata letak hunian: arah hadap, posisi pintu, kompor, kamar — diselaraskan dengan elemen bawaan Anda.</div>
  </div>
</div>

<div class="pg-section-title">
  <span class="num">1</span><span class="ttl">Cara Membaca Laporan</span><span class="hz">如 何 閱 讀</span>
</div>

<div class="pg-step-grid">
  <div class="pg-step">
    <div class="pg-step-num">01</div>
    <div class="pg-step-ttl">Tidak Perlu Berurutan</div>
    <div class="pg-step-txt">Langsung ke bab yang paling relevan dengan situasi Anda saat ini. Tiap bab dapat berdiri sendiri.</div>
  </div>
  <div class="pg-step">
    <div class="pg-step-num">02</div>
    <div class="pg-step-ttl">Cek Skor Persentase</div>
    <div class="pg-step-txt">Persentase = <strong>kecenderungan bawaan</strong>. Tinggi = kekuatan alami. Rendah = area untuk dilatih.</div>
  </div>
  <div class="pg-step">
    <div class="pg-step-num">03</div>
    <div class="pg-step-ttl">Catat &amp; Refleksi</div>
    <div class="pg-step-txt">Tandai bagian yang resonan dan yang terasa janggal. Bagan adalah titik awal, bukan titik akhir.</div>
  </div>
  <div class="pg-step">
    <div class="pg-step-num">04</div>
    <div class="pg-step-ttl">Terapkan Bertahap</div>
    <div class="pg-step-txt">Pilih 1–2 rekomendasi paling konkret dulu — feng shui, profesi, jadwal — coba 30 hari, evaluasi.</div>
  </div>
</div>

<div class="pg-section-title">
  <span class="num">2</span><span class="ttl">Skala Persentase Bawaan</span><span class="hz">百 分 尺 度</span>
</div>

<div class="pg-scale-demo">
  <div class="pg-scale-row">
    <div class="pg-scale-lbl"><strong>Kuat</strong> · 70% &amp; ke atas</div>
    <div class="pg-bar-track"><div class="pg-bar-fill high" style="width: 78%"></div></div>
    <div class="pg-scale-pct">78%</div>
    <div class="pg-scale-note">Kekuatan alami — maksimalkan tanpa banyak usaha tambahan.</div>
  </div>
  <div class="pg-scale-row">
    <div class="pg-scale-lbl"><strong>Seimbang</strong> · 50–69%</div>
    <div class="pg-bar-track"><div class="pg-bar-fill mid" style="width: 60%"></div></div>
    <div class="pg-scale-pct">60%</div>
    <div class="pg-scale-note">Cukup — bisa lebih baik dengan latihan dan lingkungan tepat.</div>
  </div>
  <div class="pg-scale-row">
    <div class="pg-scale-lbl"><strong>Perlu Dilatih</strong> · &lt; 50%</div>
    <div class="pg-bar-track"><div class="pg-bar-fill low" style="width: 35%"></div></div>
    <div class="pg-scale-pct">35%</div>
    <div class="pg-scale-note">Bukan kelemahan permanen — area untuk disiplin atau kompensasi.</div>
  </div>
</div>

<div class="pg-closing">
  <div class="pg-closing-seal">命</div>
  <div class="pg-closing-text">
    <strong>Selamat membaca.</strong> Bagan adalah <em>kompas</em>, bukan jadwal. Anda tetap pelaku utama dalam hidup Anda — kebijaksanaan, kebebasan, dan tindakan Anda yang membentuk hasil akhir.
  </div>
</div>"""


def render_pengantar(num: int, subject_name: str = "") -> str:
    return page_shell(num, "Pengantar &amp; Cara Membaca", "前 言", "PENGANTAR · 前言", PENGANTAR_BODY, subject_name)


PENGANTAR_CSS = """
/* === PENGANTAR PAGE V4.8 — port V4.6 visual === */
.pg-hero {
  display: grid; grid-template-columns: 22mm 1fr; gap: var(--sp-5); align-items: center;
  background: linear-gradient(135deg, var(--color-red) 0%, var(--color-red-deep) 100%);
  color: white; border-radius: var(--r-md); padding: var(--sp-4) var(--sp-5);
  box-shadow: 0 1.5mm 4mm rgba(139, 26, 26, 0.25);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.pg-hero-mark {
  width: 22mm; height: 22mm; border-radius: 50%;
  background: linear-gradient(135deg, var(--color-gold) 0%, #E5D3A1 100%);
  border: 0.5mm solid var(--color-gold-soft);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-serif-tc); font-size: 24pt; color: var(--color-red-deep); font-weight: 700;
  box-shadow: inset 0 0 4mm rgba(139, 26, 26, 0.15), 0 1mm 3mm rgba(0, 0, 0, 0.2);
}
.pg-hero-text { display: flex; flex-direction: column; gap: 1.5mm; }
.pg-hero-title {
  font-family: var(--font-display); font-size: 18pt; font-weight: 700;
  color: #F5EBD0; letter-spacing: 2px; line-height: 1;
}
.pg-hero-sub { font-size: 9pt; line-height: 1.5; color: white; opacity: 0.95; }
.pg-hero-sub strong { color: #F5EBD0; }

.pg-method-grid {
  display: grid; grid-template-columns: 1fr 1fr 1fr;
  gap: var(--sp-3); margin-top: var(--sp-3);
}
.pg-method-card {
  background: var(--color-paper); border: 0.3mm solid var(--color-gold-soft);
  border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4); text-align: center;
  display: grid; grid-template-rows: auto auto auto 1fr; gap: 1mm;
  box-shadow: 0 0.5mm 1.5mm rgba(0, 0, 0, 0.04);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.pg-method-card.highlight {
  border: 0.5mm solid var(--color-gold);
  background: linear-gradient(180deg, var(--color-paper) 0%, var(--color-cream-deep) 100%);
  box-shadow: 0 1.5mm 4mm rgba(201, 169, 97, 0.25);
}
.pg-method-hz {
  font-family: var(--font-serif-tc); font-size: 26pt; color: var(--color-red);
  font-weight: 700; line-height: 1; letter-spacing: 4px;
}
.pg-method-py {
  font-family: var(--font-body); font-size: 7.5pt; color: var(--color-gold-deep);
  font-style: italic; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 600;
}
.pg-method-id {
  font-family: var(--font-display); font-size: 10pt; color: var(--color-ink);
  font-weight: 600; letter-spacing: 0.5px; padding: 1mm 0;
  border-top: 0.2mm solid var(--color-gold-soft);
  border-bottom: 0.2mm solid var(--color-gold-soft);
}
.pg-method-desc { font-size: 7.8pt; line-height: 1.45; color: var(--color-ink); padding-top: 1mm; }
.pg-method-desc strong { color: var(--color-red); }

.pg-section-title {
  display: grid; grid-template-columns: 8mm 1fr auto; gap: var(--sp-4); align-items: baseline;
  border-bottom: 0.4mm solid var(--color-gold); padding-bottom: 1.5mm;
  margin: var(--sp-4) 0 var(--sp-2) 0;
}
.pg-section-title .num {
  font-family: var(--font-display); font-size: 18pt; color: var(--color-gold);
  font-weight: 700; line-height: 1;
}
.pg-section-title .ttl {
  font-family: var(--font-display); font-size: 13pt; color: var(--color-red);
  letter-spacing: 1px; font-weight: 600;
}
.pg-section-title .hz {
  font-family: var(--font-serif-tc); font-size: 11pt; color: var(--color-muted);
  letter-spacing: 3px;
}

.pg-step-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: var(--sp-3); }
.pg-step {
  background: var(--color-paper); border-left: 1.2mm solid var(--color-gold);
  border-radius: 0 var(--r-sm) var(--r-sm) 0; padding: var(--sp-2) var(--sp-3);
  display: grid; grid-template-rows: auto auto 1fr; gap: 1mm;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.pg-step-num {
  font-family: var(--font-display); font-size: 18pt; color: var(--color-gold-deep);
  font-weight: 700; line-height: 1; letter-spacing: 1px;
}
.pg-step-ttl {
  font-family: var(--font-body); font-size: 8.5pt; color: var(--color-red);
  font-weight: 700; letter-spacing: 0.5px; line-height: 1.2;
}
.pg-step-txt { font-size: 7.5pt; line-height: 1.45; color: var(--color-ink); }
.pg-step-txt strong { color: var(--color-red); }

.pg-scale-demo {
  display: flex; flex-direction: column; gap: var(--sp-3);
  padding: var(--sp-3) var(--sp-4); background: var(--color-paper);
  border: 0.3mm solid var(--color-gold-soft); border-radius: var(--r-md);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.pg-scale-row {
  display: grid; grid-template-columns: 38mm 1fr 12mm; gap: var(--sp-3);
  grid-template-rows: auto auto; align-items: center;
}
.pg-scale-row .pg-scale-lbl { font-size: 8.5pt; color: var(--color-ink); grid-row: 1; }
.pg-scale-row .pg-scale-lbl strong { color: var(--color-red); }
.pg-scale-row .pg-bar-track {
  grid-row: 1; height: 4mm;
  background: rgba(201, 169, 97, 0.18); border-radius: 0.8mm; overflow: hidden;
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.pg-scale-row .pg-bar-fill {
  height: 100%; border-radius: 0.8mm;
  background: linear-gradient(90deg, var(--color-gold) 0%, #E5D3A1 100%);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.pg-scale-row .pg-bar-fill.high {
  background: linear-gradient(90deg, var(--color-success) 0%, #8FBE8C 100%);
}
.pg-scale-row .pg-bar-fill.mid {
  background: linear-gradient(90deg, var(--color-gold) 0%, #E5D3A1 100%);
}
.pg-scale-row .pg-bar-fill.low {
  background: linear-gradient(90deg, var(--color-warn) 0%, #D8A582 100%);
}
.pg-scale-row .pg-scale-pct {
  grid-row: 1; font-family: var(--font-display); font-weight: 700; font-size: 11pt;
  color: var(--color-red); text-align: right;
}
.pg-scale-row .pg-scale-note {
  grid-column: 1 / -1; grid-row: 2; font-size: 7.5pt; color: var(--color-muted);
  font-style: italic; line-height: 1.35;
}

.pg-closing {
  display: grid; grid-template-columns: 16mm 1fr; gap: var(--sp-4); align-items: center;
  background: linear-gradient(135deg, var(--color-gold-tint) 0%, var(--color-paper) 100%);
  border: 0.3mm solid var(--color-gold); border-radius: var(--r-md);
  padding: var(--sp-3) var(--sp-4); margin-top: var(--sp-3);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.pg-closing-seal {
  width: 16mm; height: 16mm; border-radius: 1.5mm;
  background: var(--color-red); color: #F5EBD0;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-serif-tc); font-size: 22pt; font-weight: 700;
  transform: rotate(-3deg);
  box-shadow: 0 1mm 3mm rgba(139, 26, 26, 0.3);
  print-color-adjust: exact; -webkit-print-color-adjust: exact;
}
.pg-closing-text { font-size: 9pt; line-height: 1.55; color: var(--color-ink); }
.pg-closing-text strong { color: var(--color-red); }
.pg-closing-text em { color: var(--color-gold-deep); font-style: italic; }
"""
