# export_pdf.ps1 — Build master HTML + export Henry's report PDF
# Usage: powershell -ExecutionPolicy Bypass -File C:\temp\trial\export_pdf.ps1
# Run this anytime after editing source page_*.html files. Source files NOT modified.

$ErrorActionPreference = 'Stop'
$src    = "C:\temp\trial"
$outPdf = "C:\Users\sukam\OneDrive\Documents\Ramalan\Henry_Ramalan_Lengkap.pdf"
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) {
  $chrome = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
}

# Page order (23 pages)
$files = @(
  "page_01_cover.html","page_02_toc.html","page_03_intro.html",
  "page_profile.html","page_05_bazi_opener.html","page_06_daymaster.html",
  "page_marriage.html","page_08_xingqing.html","page_09_family.html",
  "page_10_shensha.html","page_11_caifu.html","page_career.html",
  "page_yangzhai.html","page_dayun.html","page_15_ziwei_opener.html",
  "page_ziwei.html","page_17_palace1.html","page_18_palace2.html",
  "page_19_palace3.html","page_20_kesimpulan.html","page_synthesis.html",
  "page_22_glossary.html","page_23_disclaimer.html"
)

# Build absolute file:// URL prefix (Chrome PDF needs absolute for SVG <image>)
$srcUrl = ($src -replace '\\','/' -replace '^([A-Za-z]):','file:///$1:') + '/'
$cssUrl = $srcUrl + 'style.css'

Write-Host "[1/3] Building master HTML..." -ForegroundColor Cyan
$styles = ""
$bodies = ""
foreach ($f in $files) {
  $path = "$src\$f"
  if (-not (Test-Path $path)) { Write-Warning "Missing: $f"; continue }
  $content = Get-Content $path -Raw -Encoding UTF8

  # Extract <style> block
  if ($content -match '(?s)<style>(.*?)</style>') {
    $styles += "`r`n/* === $f === */`r`n" + $matches[1] + "`r`n"
  }

  # Extract <body>...</body>
  if ($content -match '(?s)<body[^>]*>(.*?)</body>') {
    $body = $matches[1]

    # CRITICAL FIX: Convert relative SVG/img refs to absolute file:// URLs
    # This is what makes images render correctly in Chrome PDF
    $body = [regex]::Replace($body, 'src="([^/"][^":]*\.(svg|png|jpg|jpeg))"', { param($m) 'src="' + $srcUrl + $m.Groups[1].Value + '"' })
    $body = [regex]::Replace($body, 'href="([^/"][^":]*\.(svg|png|jpg|jpeg))"', { param($m) 'href="' + $srcUrl + $m.Groups[1].Value + '"' })

    $bodies += $body + "`r`n"
  }
}

$master = @"
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Henry — Laporan Ramalan Lengkap (PDF)</title>
<link rel="stylesheet" href="$cssUrl">
<style>
$styles

/* PDF EXPORT — emoji fallback + page break */
.ind-icon, .toc-row .ico, .pal-action .ico, .dc-item .ico, .xqc-item .ico {
  font-family: 'Segoe UI Emoji','Segoe UI Symbol','Inter',system-ui,sans-serif !important;
}

@page { size: A4 portrait; margin: 0; }
html, body { background: white !important; margin: 0 !important; padding: 0 !important; }
.page {
  page-break-after: always !important;
  page-break-inside: avoid !important;
  margin: 0 !important;
  box-shadow: none !important;
}
.page:last-child { page-break-after: auto !important; }
</style>
</head>
<body>
$bodies
</body>
</html>
"@

$masterFile = "$src\report_henry_full.html"
[System.IO.File]::WriteAllText($masterFile, $master, [System.Text.UTF8Encoding]::new($false))
$mSize = [math]::Round((Get-Item $masterFile).Length / 1KB, 1)
Write-Host "      Master HTML: $mSize KB" -ForegroundColor Gray

Write-Host "[2/3] Running Chrome headless..." -ForegroundColor Cyan
$srcFile = ($masterFile -replace '\\','/' -replace '^([A-Za-z]):','file:///$1:')

# Write to temp first, then move (avoids 'file locked' error if PDF is open in viewer)
$tempPdf = Join-Path $env:TEMP ("henry_pdf_" + [guid]::NewGuid().ToString().Substring(0,8) + ".pdf")

$prevEAP = $ErrorActionPreference
$ErrorActionPreference = 'SilentlyContinue'
& $chrome `
  --headless `
  --disable-gpu `
  --no-sandbox `
  --allow-file-access-from-files `
  --virtual-time-budget=5000 `
  --run-all-compositor-stages-before-draw `
  --print-to-pdf=$tempPdf `
  --no-pdf-header-footer `
  $srcFile 2>&1 | Out-Null
$ErrorActionPreference = $prevEAP
Start-Sleep -Seconds 1

Write-Host "[3/3] Moving to final location..." -ForegroundColor Cyan
if (-not (Test-Path $tempPdf)) {
  Write-Host "  [FAIL] Chrome did not produce PDF" -ForegroundColor Red
  exit 1
}

$finalPdf = $outPdf
try {
  Move-Item $tempPdf $finalPdf -Force -ErrorAction Stop
} catch {
  # File locked (likely open in viewer) - save as timestamped variant
  $stamp = Get-Date -Format "HHmmss"
  $finalPdf = $outPdf -replace '\.pdf$', "_$stamp.pdf"
  Move-Item $tempPdf $finalPdf -Force
  Write-Host "  [WARN] Original locked (close PDF viewer to overwrite)." -ForegroundColor Yellow
  Write-Host "         Saved as: $finalPdf" -ForegroundColor Yellow
}

if (Test-Path $finalPdf) {
  $sz = [math]::Round((Get-Item $finalPdf).Length / 1KB, 1)
  Write-Host ""
  Write-Host "  [OK] PDF ready" -ForegroundColor Green
  Write-Host "    File: $finalPdf"
  Write-Host "    Size: $sz KB"
  Write-Host ""
}
