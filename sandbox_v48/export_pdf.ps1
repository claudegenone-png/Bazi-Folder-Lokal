# V4.8 Export HTML → PDF
# Usage: powershell -File export_pdf.ps1 <html_path> <output_pdf_path>
# Or with subject info: powershell -File export_pdf.ps1 <html_path> <name> <hanzi> <birth>
#                       → output to #result/{date}/{Name}-{Hanzi}-{Birth}.pdf

$ErrorActionPreference = 'Stop'

$htmlPath = $args[0]
if (-not $htmlPath -or -not (Test-Path -LiteralPath $htmlPath)) {
  Write-Error "Usage: export_pdf.ps1 <html_path> <output_pdf>  OR  <html_path> <name> <hanzi> <birth>"
  exit 1
}

if ($args.Count -eq 2) {
  $pdfPath = $args[1]
} elseif ($args.Count -eq 4) {
  $name = $args[1]; $hanzi = $args[2]; $birth = $args[3]
  $today = Get-Date -Format "yyyy-MM-dd"
  $resultDir = Join-Path $env:USERPROFILE "OneDrive\Documents\Ramalan\#result\$today"
  if (-not (Test-Path -LiteralPath $resultDir)) { New-Item -ItemType Directory -Force -Path $resultDir | Out-Null }
  $nameDashed = $name -replace ' ', '-'
  $pdfPath = Join-Path $resultDir "$nameDashed-$hanzi-$birth.pdf"
} else {
  Write-Error "Wrong args. Need 2 (html, pdf) or 4 (html, name, hanzi, birth)."
  exit 1
}

# Find Chrome
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) {
  $chrome = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
}
if (-not (Test-Path $chrome)) { Write-Error "Chrome/Edge not found"; exit 1 }

# Build file:// URL with %23 encoding for # (CRITICAL — # in path = URL fragment)
$absPath = (Resolve-Path -LiteralPath $htmlPath).Path
$url = "file:///" + ($absPath -replace '\\','/' -replace '#','%23')

# Render to temp first (avoids file lock if PDF open in viewer)
$tmpPdf = Join-Path $env:TEMP ("v48_pdf_" + [guid]::NewGuid().ToString().Substring(0,8) + ".pdf")

Write-Host "[1/2] Running Chrome headless..." -ForegroundColor Cyan
Write-Host "      Source URL: $url" -ForegroundColor DarkGray

$prevEAP = $ErrorActionPreference
$ErrorActionPreference = 'SilentlyContinue'
& $chrome `
  --headless `
  --disable-gpu `
  --no-sandbox `
  --virtual-time-budget=30000 `
  --run-all-compositor-stages-before-draw `
  --no-pdf-header-footer `
  --print-to-pdf=$tmpPdf `
  $url 2>&1 | Out-Null
$ErrorActionPreference = $prevEAP

Start-Sleep -Seconds 1
if (-not (Test-Path $tmpPdf)) { Write-Error "Chrome did not produce PDF"; exit 1 }

Write-Host "[2/2] Moving to final location..." -ForegroundColor Cyan
$finalPdf = $pdfPath
try {
  if (Test-Path -LiteralPath $finalPdf) { Remove-Item -LiteralPath $finalPdf -Force }
  Move-Item -LiteralPath $tmpPdf -Destination $finalPdf -Force
} catch {
  $stamp = Get-Date -Format "HHmmss"
  $finalPdf = $pdfPath -replace '\.pdf$', "_$stamp.pdf"
  Move-Item -LiteralPath $tmpPdf -Destination $finalPdf -Force
  Write-Host "  [WARN] Original locked. Saved as: $finalPdf" -ForegroundColor Yellow
}

if (Test-Path -LiteralPath $finalPdf) {
  $sz = [math]::Round((Get-Item -LiteralPath $finalPdf).Length / 1KB, 1)
  Write-Host ""
  Write-Host "  [OK] PDF ready" -ForegroundColor Green
  Write-Host "    File: $finalPdf"
  Write-Host "    Size: $sz KB"
  Write-Host ""
}
