# export_pdf.ps1 — Build master HTML + export Lin Ru Yi's report PDF
$ErrorActionPreference = 'Stop'
$src    = "C:\Users\sukam\OneDrive\Documents\Ramalan\cache\linruyi"
$today  = Get-Date -Format "yyyy-MM-dd"
$outDir = "C:\Users\sukam\OneDrive\Documents\Ramalan\#result\$today"
$outPdf = Join-Path $outDir "Lin-Ru-Yi-林如意-1995-05-30.pdf"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) {
  $chrome = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
}

$shared = "C:\Users\sukam\OneDrive\Documents\Ramalan\cache\_shared"

# Each entry: [filename, source-folder]. Templated pages load from _shared/ (not personalized per subject).
$files = @(
  @("page_01_cover.html",       $src),
  @("tpl_toc.html",             $shared),
  @("page_03_intro.html",       $src),
  @("page_profile.html",        $src),
  @("tpl_bab_bazi.html",        $shared),
  @("page_06_daymaster.html",   $src),
  @("page_marriage.html",       $src),
  @("page_08_xingqing.html",    $src),
  @("page_09_family.html",      $src),
  @("page_10_shensha.html",     $src),
  @("page_11_caifu.html",       $src),
  @("page_career.html",         $src),
  @("page_yangzhai.html",       $src),
  @("page_dayun.html",          $src),
  @("tpl_bab_ziwei.html",       $shared),
  @("page_ziwei.html",          $src),
  @("page_17_palace1.html",     $src),
  @("page_18_palace2.html",     $src),
  @("page_19_palace3.html",     $src),
  @("page_20_kesimpulan.html",  $src),
  @("page_synthesis.html",      $src),
  @("tpl_glossary.html",        $shared),
  @("tpl_disclaimer.html",      $shared)
)

$srcUrl = ($src -replace '\\','/' -replace '^([A-Za-z]):','file:///$1:') + '/'
$cssUrl = $srcUrl + 'style.css'

Write-Host "[1/3] Building master HTML..." -ForegroundColor Cyan
$styles = ""
$bodies = ""
foreach ($entry in $files) {
  $f = $entry[0]; $folder = $entry[1]
  $path = Join-Path $folder $f
  if (-not (Test-Path $path)) { Write-Warning "Missing: $path"; continue }
  $content = Get-Content $path -Raw -Encoding UTF8
  if ($content -match '(?s)<style>(.*?)</style>') {
    $styles += "`r`n/* === $f === */`r`n" + $matches[1] + "`r`n"
  }
  if ($content -match '(?s)<body[^>]*>(.*?)</body>') {
    $body = $matches[1]
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
<title>Lin Ru Yi — Laporan Ramalan Lengkap (PDF)</title>
<link rel="stylesheet" href="$cssUrl">
<style>
$styles

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

$masterFile = "$src\report_linruyi_full.html"
[System.IO.File]::WriteAllText($masterFile, $master, [System.Text.UTF8Encoding]::new($false))
$mSize = [math]::Round((Get-Item $masterFile).Length / 1KB, 1)
Write-Host "      Master HTML: $mSize KB" -ForegroundColor Gray

Write-Host "[2/3] Running Chrome headless..." -ForegroundColor Cyan
$srcFile = ($masterFile -replace '\\','/' -replace '^([A-Za-z]):','file:///$1:')
$tempPdf = Join-Path $env:TEMP ("linruyi_pdf_" + [guid]::NewGuid().ToString().Substring(0,8) + ".pdf")

$prevEAP = $ErrorActionPreference
$ErrorActionPreference = 'SilentlyContinue'
& $chrome `
  --headless `
  --disable-gpu `
  --no-sandbox `
  --allow-file-access-from-files `
  --virtual-time-budget=8000 `
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
  $stamp = Get-Date -Format "HHmmss"
  $finalPdf = $outPdf -replace '\.pdf$', "_$stamp.pdf"
  Move-Item $tempPdf $finalPdf -Force
  Write-Host "  [WARN] Original locked. Saved as: $finalPdf" -ForegroundColor Yellow
}

if (Test-Path $finalPdf) {
  $sz = [math]::Round((Get-Item $finalPdf).Length / 1KB, 1)
  Write-Host ""
  Write-Host "  [OK] PDF ready" -ForegroundColor Green
  Write-Host "    File: $finalPdf"
  Write-Host "    Size: $sz KB"
}
