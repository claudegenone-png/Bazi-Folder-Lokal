# PDF Template — HTML + CSS untuk Laporan Ramalan Klasik Tionghoa

Reference template untuk render PDF cantik dari hasil transkrip foto.

**ITERASI 2 — FIXES (request user setelah test pertama):**

1. ❗ MARGIN/CROP — banyak element melebihi paper (paling penting)
2. 🎨 Lebih banyak grafik/gambar/element variatif
3. 📁 SVG path: `C:\Users\josuk\OneDrive\Documents\Ramalan\SVG Shio\V2\`
4. 🚫 Hapus karakter China di footer kiri-kanan tiap halaman

## Workflow Convert ke PDF

### Step 1: Generate `report.html`

Skill akan generate file HTML dengan struktur di bawah, diisi data dari foto.

### Step 2: Audit dengan web-design-guidelines

Sebelum render PDF, jalankan audit untuk catch overflow & contrast issues.

### Step 3: Convert ke PDF pakai Chrome Headless

Path Chrome di Windows umumnya:
```
C:\Program Files\Google\Chrome\Application\chrome.exe
```

Command:
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" \
  --headless \
  --disable-gpu \
  --no-margins \
  --print-to-pdf="C:\path\to\Ramalan_Subjek.pdf" \
  --no-pdf-header-footer \
  "file:///C:/path/to/report.html"
```

## CSS Master Template (FIXED MARGIN + NO FOOTER HANZI)

```css
/* === FONT IMPORTS === */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900&family=Noto+Serif:ital,wght@0,400;0,700;1,400&family=Ma+Shan+Zheng&display=swap');

/* === GLOBAL RESET (CRITICAL untuk fix overflow) === */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  max-width: 100%;
}

html, body {
  font-family: 'Noto Serif', 'Noto Serif TC', serif;
  color: #2a1a0a;
  background: #f7f0e0;
  width: 210mm;
  margin: 0 auto;
  overflow-x: hidden;          /* prevent horizontal scroll */
}

/* === COLOR PALETTE === */
:root {
  --red-imperial: #b91c1c;
  --red-deep: #7a0d0d;
  --gold-rich: #c9a04c;
  --gold-light: #e8c87a;
  --paper-cream: #f7f0e0;
  --paper-aged: #ede0bf;
  --ink-black: #2a1a0a;
  --ink-gray: #5c4a36;
}

/* === @PAGE SETUP (KRUSIAL untuk PDF) === */
@page {
  size: A4 portrait;
  margin: 0;                   /* margin diatur di .page padding */
}

@media print {
  body { background: white !important; }
  .page {
    page-break-after: always;
    break-after: page;
  }
  .page:last-child { page-break-after: auto; }
}

/* === PAGE BASE — PADDING 20mm SAFE-ZONE === */
.page {
  position: relative;
  width: 210mm;
  height: 297mm;
  padding: 20mm 18mm 18mm;     /* TOP RIGHT-LEFT BOTTOM — leave room for borders */
  background: var(--paper-cream);
  overflow: hidden;            /* CRITICAL: clip apa pun yang overflow */
  page-break-after: always;
}

/* Bingkai ornamen — INSET dari edge, BUKAN tabrakan dengan content */
.page::before {
  content: '';
  position: absolute;
  inset: 10mm;                 /* 10mm dari edge halaman */
  border: 2px solid var(--red-imperial);
  pointer-events: none;
  z-index: 0;
}

.page::after {
  content: '';
  position: absolute;
  inset: 12mm;                 /* 12mm dari edge halaman */
  border: 1px solid var(--gold-rich);
  pointer-events: none;
  z-index: 0;
}

/* Content harus DI ATAS bingkai (z-index) dan dalam safe-zone */
.page > * {
  position: relative;
  z-index: 1;
  max-width: 100%;
}

/* === CONTENT AREA — STRICT max-width === */
.content {
  max-width: 174mm;            /* 210 - 18*2 = 174 mm */
  margin: 0 auto;
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}

/* === HEADINGS === */
h1, h2, h3, h4 {
  font-family: 'Noto Serif TC', serif;
  color: var(--red-imperial);
  margin-bottom: 6mm;
  text-align: center;
  word-break: break-word;
  overflow-wrap: anywhere;
}

h1 { font-size: 28pt; letter-spacing: 4px; }
h2 { font-size: 22pt; letter-spacing: 3px; border-bottom: 2px solid var(--gold-rich); padding-bottom: 3mm; }
h3 { font-size: 16pt; color: var(--red-deep); margin-top: 4mm; }
h4 { font-size: 13pt; color: var(--ink-gray); }

/* === PARAGRAPH === */
p {
  font-size: 11pt;
  line-height: 1.7;
  margin-bottom: 3mm;
  text-align: justify;
  word-break: break-word;
  hyphens: auto;
}

/* === HANZI QUOTE === */
.hanzi-quote {
  font-family: 'Noto Serif TC', serif;
  font-size: 13pt;
  line-height: 1.9;
  background: rgba(232, 200, 122, 0.15);
  border-left: 3px solid var(--red-imperial);
  padding: 4mm 6mm;
  margin: 4mm 0;
  word-break: break-all;       /* Hanzi kadang panjang */
  line-break: anywhere;
  max-width: 100%;
}

/* === TABLE — fixed layout untuk prevent overflow === */
table {
  width: 100%;
  max-width: 100%;
  border-collapse: collapse;
  table-layout: fixed;         /* CRITICAL: fix kolom width */
  margin: 4mm 0;
}

table th, table td {
  padding: 2.5mm 3mm;
  border: 1px solid var(--gold-rich);
  text-align: center;
  word-wrap: break-word;
  overflow-wrap: break-word;
  font-size: 10pt;
  vertical-align: middle;
}

table th {
  background: var(--red-imperial);
  color: var(--paper-cream);
  font-weight: 700;
}

/* === IMG / SVG — never overflow === */
img, svg {
  max-width: 100%;
  height: auto;
  display: block;
}

.chart-container {
  max-width: 140mm;            /* leave breathing room */
  margin: 4mm auto;
  text-align: center;
}

.chart-container svg {
  width: 100%;
  height: auto;
  max-height: 100mm;
}

/* === SHIO ICONS === */
.shio-icon {
  width: 70mm;                 /* default cover size */
  height: auto;
}

.shio-icon-medium { width: 35mm; }
.shio-icon-small  { width: 18mm; }

/* === COVER === */
.page.cover {
  background: linear-gradient(135deg, #8b0a0a 0%, #b91c1c 50%, #8b0a0a 100%);
  color: var(--paper-cream);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.page.cover::before { border-color: var(--gold-rich); }
.page.cover::after  { border-color: var(--gold-light); }

.cover-frame { z-index: 1; max-width: 160mm; }

.hanzi-large {
  font-family: 'Ma Shan Zheng', cursive;
  font-size: 140pt;
  color: var(--gold-rich);
  line-height: 1;
  margin-bottom: 12mm;
  text-shadow: 0 0 15px rgba(232, 200, 122, 0.5);
}

.cover-title { font-size: 32pt; margin-bottom: 6mm; }
.cover-subtitle { font-size: 20pt; font-style: italic; color: var(--gold-light); }
.cover-meta { font-size: 12pt; color: var(--paper-aged); margin: 4mm 0 20mm; }
.cover-tagline {
  font-family: 'Ma Shan Zheng', cursive;
  font-size: 16pt;
  color: var(--gold-rich);
  letter-spacing: 6px;
}

/* === FOOTER (TANPA HANZI — request user) === */
.page-footer {
  position: absolute;
  bottom: 14mm;
  left: 18mm;
  right: 18mm;
  display: flex;
  justify-content: center;     /* CENTER ONLY — no left/right Hanzi */
  align-items: center;
  font-size: 9pt;
  color: var(--gold-rich);
  z-index: 1;
}

.page-footer::before {
  content: '';
  position: absolute;
  top: -2mm;
  left: 50%;
  transform: translateX(-50%);
  width: 40mm;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-rich), transparent);
}

.page-number {
  font-family: 'Noto Serif', serif;
  letter-spacing: 2px;
  padding: 0 4mm;
}

/* Optional ornament separator (BUKAN Hanzi) */
.page-footer .ornament {
  font-size: 12pt;
  color: var(--gold-light);
  margin: 0 6mm;
}

/* === PAGE HEADER === */
.page-header {
  position: absolute;
  top: 14mm;
  left: 18mm;
  right: 18mm;
  text-align: center;
  font-size: 10pt;
  color: var(--gold-rich);
  letter-spacing: 3px;
  border-bottom: 1px solid var(--gold-light);
  padding-bottom: 2mm;
  z-index: 1;
}

/* === CHAPTER DIVIDER === */
.page.chapter-divider {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background: linear-gradient(180deg, var(--paper-cream) 0%, var(--paper-aged) 100%);
}

.chapter-mark {
  font-family: 'Ma Shan Zheng', cursive;
  font-size: 28pt;
  color: var(--gold-rich);
  margin-bottom: 8mm;
  letter-spacing: 6px;
}

.chapter-title { font-size: 40pt; color: var(--red-imperial); border: none; }
.chapter-subtitle {
  font-size: 14pt;
  font-style: italic;
  color: var(--ink-gray);
  letter-spacing: 3px;
  margin-top: 4mm;
}

/* === INFOGRAPHIC CARD GRID (variasi visual baru) === */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 4mm;
  margin: 4mm 0;
  max-width: 100%;
}

.info-grid-3 { grid-template-columns: repeat(3, 1fr); }

.info-card {
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid var(--gold-rich);
  border-radius: 2mm;
  padding: 3mm 4mm;
  font-size: 10pt;
  overflow: hidden;
}

.info-card-title {
  font-weight: 700;
  color: var(--red-imperial);
  font-size: 11pt;
  margin-bottom: 1mm;
}

/* === TIMELINE (untuk 大運) === */
.timeline {
  position: relative;
  padding-left: 6mm;
  margin: 4mm 0;
}

.timeline::before {
  content: '';
  position: absolute;
  top: 0;
  left: 2mm;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, var(--gold-rich), var(--red-imperial));
}

.timeline-item {
  position: relative;
  padding-bottom: 4mm;
  font-size: 10pt;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -5.5mm;
  top: 1mm;
  width: 3mm;
  height: 3mm;
  background: var(--red-imperial);
  border: 1px solid var(--gold-rich);
  border-radius: 50%;
}

/* === BAGUA DIAGRAM HOLDER === */
.bagua-wrap {
  width: 110mm;
  height: 110mm;
  margin: 4mm auto;
  position: relative;
}

.bagua-wrap svg { width: 100%; height: 100%; }

/* === ZIWEI 12-PALACE GRID === */
.ziwei-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(4, 1fr);
  gap: 0.5mm;
  width: 160mm;
  max-width: 100%;
  height: 160mm;
  margin: 4mm auto;
  background: var(--gold-rich);
  border: 2px solid var(--red-imperial);
}

.palace-cell {
  background: var(--paper-cream);
  padding: 1.5mm;
  font-size: 7.5pt;
  font-family: 'Noto Serif TC', serif;
  overflow: hidden;
  word-break: break-all;
}

.palace-cell.center {
  grid-column: 2 / 4;
  grid-row: 2 / 4;
  background: var(--red-imperial);
  color: var(--paper-cream);
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

/* === BLOCKQUOTE === */
blockquote {
  border-left: 3px solid var(--red-imperial);
  padding: 2mm 5mm;
  margin: 3mm 0;
  font-style: italic;
  color: var(--ink-gray);
  background: rgba(232, 200, 122, 0.08);
  font-size: 10.5pt;
}

/* === LIST === */
ul, ol {
  padding-left: 6mm;
  margin: 3mm 0;
  font-size: 10.5pt;
}

li { margin-bottom: 1.5mm; line-height: 1.6; }

/* === STRONG / EM === */
strong { color: var(--red-deep); }
em { color: var(--gold-rich); font-style: italic; }
```

## HTML Skeleton (Updated)

```html
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Ramalan {{NAMA}}</title>
<style>/* CSS injected here */</style>
</head>
<body>

<!-- HALAMAN 1: COVER -->
<section class="page cover">
  <div class="cover-frame">
    <!-- SVG shio MERAH user (lihat ASET) -->
    <div class="shio-icon" style="margin: 0 auto 8mm;">
      {{INLINE_SVG_SHIO_MERAH}}
    </div>
    <h1 class="cover-title">命理分析報告</h1>
    <p class="cover-subtitle">Ramalan Nasib<br>{{NAMA_INDONESIA}}</p>
    <p class="cover-meta">{{TANGGAL_LAHIR}} · {{JAM}} · {{SHIO_HANZI}}</p>
    <p class="cover-tagline">八字 · 紫微 · 陽宅</p>
  </div>
</section>

<!-- HALAMAN 7: 性情 (CONTOH content page) -->
<section class="page">
  <div class="page-header">第一章 · 性情 · Kepribadian</div>

  <div class="content">
    <h2>性情 (Kepribadian)</h2>

    <div class="hanzi-quote">
      {{HANZI_TRANSCRIPT_FROM_PHOTO}}
    </div>

    <p>{{INDONESIA_TRANSLATION}}</p>

    <!-- Infographic card 4-quadrant — variasi baru -->
    <div class="info-grid">
      <div class="info-card">
        <div class="info-card-title">💎 Kekuatan</div>
        <ul>
          <li>{{strength_1}}</li>
          <li>{{strength_2}}</li>
        </ul>
      </div>
      <div class="info-card">
        <div class="info-card-title">🌱 Area Tumbuh</div>
        <ul>
          <li>{{growth_1}}</li>
          <li>{{growth_2}}</li>
        </ul>
      </div>
      <div class="info-card">
        <div class="info-card-title">💬 Komunikasi</div>
        <p>{{communication_style}}</p>
      </div>
      <div class="info-card">
        <div class="info-card-title">⚡ Action</div>
        <p>{{action_style}}</p>
      </div>
    </div>
  </div>

  <!-- Footer TANPA Hanzi (FIXED) -->
  <div class="page-footer">
    <span class="page-number">7 / 30</span>
  </div>
</section>

<!-- HALAMAN 12: 事業 dengan Wu Xing radar chart -->
<section class="page">
  <div class="page-header">第一章 · 事業 · Karir & Profesi</div>
  <div class="content">
    <h2>事業 (Karir)</h2>

    <!-- Wu Xing radar chart dari data-visualization -->
    <div class="chart-container">
      {{INLINE_SVG_WU_XING_RADAR}}
    </div>

    <h3>Industri Cocok</h3>
    <div class="info-grid info-grid-3">
      <div class="info-card">
        <div class="info-card-title">🌳 Kayu</div>
        <p>{{kayu_industries}}</p>
      </div>
      <div class="info-card">
        <div class="info-card-title">💧 Air</div>
        <p>{{air_industries}}</p>
      </div>
      <div class="info-card">
        <div class="info-card-title">🔥 Api</div>
        <p>{{api_industries}}</p>
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span class="page-number">12 / 30</span>
  </div>
</section>

<!-- HALAMAN 11: 婚配 dengan compatibility wheel -->
<section class="page">
  <div class="page-header">第一章 · 婚配 · Kompatibilitas</div>
  <div class="content">
    <h2>婚配 (Kompatibilitas Pernikahan)</h2>

    <!-- Compatibility wheel chart dari data-visualization -->
    <div class="chart-container">
      {{INLINE_SVG_COMPATIBILITY_WHEEL}}
    </div>

    <!-- Grid SVG shio besar -->
    <div style="display: flex; justify-content: center; gap: 6mm; margin: 4mm 0;">
      <div class="shio-icon-medium">{{SVG_SHIO_COMPATIBLE_1_MERAH}}</div>
      <div class="shio-icon-medium">{{SVG_SHIO_COMPATIBLE_2_MERAH}}</div>
      <div class="shio-icon-medium">{{SVG_SHIO_COMPATIBLE_3_MERAH}}</div>
    </div>
    <p style="text-align: center; font-size: 10pt;">三合 · Trinitas Harmoni</p>
  </div>
  <div class="page-footer">
    <span class="page-number">11 / 30</span>
  </div>
</section>

</body>
</html>
```

## SVG Charts Referensi (untuk data-visualization)

### Wu Xing Radar Chart (5 Elemen)

```svg
<svg class="wuxing-radar" viewBox="0 0 200 200" preserveAspectRatio="xMidYMid meet">
  <!-- Pentagon background -->
  <polygon points="100,20 175,75 145,170 55,170 25,75"
           fill="none" stroke="#c9a04c" stroke-width="0.8"/>
  <!-- Inner rings (25% 50% 75%) -->
  <polygon points="100,40 156,80 134,150 66,150 44,80"
           fill="none" stroke="#c9a04c" stroke-width="0.4" opacity="0.6"/>
  <!-- Data polygon (sample) -->
  <polygon points="100,30 165,77 140,160 60,160 35,77"
           fill="rgba(185,28,28,0.3)" stroke="#b91c1c" stroke-width="1.5"/>
  <!-- Labels -->
  <text x="100" y="15" text-anchor="middle" font-family="Noto Serif TC" font-size="11" fill="#7a0d0d">木 Kayu</text>
  <text x="180" y="78" text-anchor="middle" font-size="11" fill="#7a0d0d">火 Api</text>
  <text x="150" y="180" text-anchor="middle" font-size="11" fill="#7a0d0d">土 Tanah</text>
  <text x="50" y="180" text-anchor="middle" font-size="11" fill="#7a0d0d">金 Logam</text>
  <text x="20" y="78" text-anchor="middle" font-size="11" fill="#7a0d0d">水 Air</text>
</svg>
```

### Compatibility Wheel (12 Shio)

```svg
<svg viewBox="0 0 220 220" preserveAspectRatio="xMidYMid meet">
  <circle cx="110" cy="110" r="90" fill="none" stroke="#c9a04c" stroke-width="1"/>
  <circle cx="110" cy="110" r="60" fill="none" stroke="#c9a04c" stroke-width="0.5"/>
  <!-- 12 segment lines -->
  <!-- repeat for each angle: 0, 30, 60, ... 330 -->
  <!-- subject shio in center, compatible shio in green ring, conflict shio in red ring -->
</svg>
```

### 大運 Timeline Chart

Use HTML timeline class instead of SVG (more flexible):

```html
<div class="timeline">
  <div class="timeline-item">
    <strong>戊申</strong> (4-13 thn) — 1962-1971
    <p style="font-size: 9pt; color: var(--ink-gray);">Awal kehidupan, pendidikan dasar</p>
  </div>
  <div class="timeline-item">
    <strong>己酉</strong> (14-23 thn) — 1972-1981
    <p style="font-size: 9pt; color: var(--ink-gray);">Masa remaja, formasi karakter</p>
  </div>
  <!-- ... 8 more steps ... -->
</div>
```

## Important Reminders

1. **Test before render**: buka `report.html` di Chrome, lihat preview A4 print
   (`Ctrl+P` → Save as PDF). Cek tiap halaman.
2. **Margin safe-zone**: content max-width 174mm di halaman 210mm A4.
3. **No JavaScript**: PDF statis, JS gak akan jalan.
4. **Footer rule**: HANYA nomor halaman tengah, **TIDAK ADA Hanzi character**
   di kiri-kanan.
5. **Charts**: pakai data-visualization skill untuk render SVG, jangan ngarang
   sendiri.
6. **Audit**: web-design-guidelines skill harus dipanggil sebelum convert PDF.
