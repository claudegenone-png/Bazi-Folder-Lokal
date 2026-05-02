# V4.6 FINAL test run — Iran 11-40 folder
# Usage: $env:ANTHROPIC_API_KEY="sk-ant-..."; .\run_iran_test.ps1
# Atau set env permanent: setx ANTHROPIC_API_KEY "sk-ant-..." (restart PS)

$ErrorActionPreference = "Stop"

if (-not $env:ANTHROPIC_API_KEY) {
    Write-Error "ANTHROPIC_API_KEY tidak set. Run: `$env:ANTHROPIC_API_KEY='sk-ant-...'"
    exit 1
}

$photos = "C:\Users\sukam\OneDrive\Documents\Bawn\Project\Long\5. Iran SHot Passenger Plane\#foto\#database\11-40"
$sid = "iran_11_40"

Set-Location "C:\Users\sukam\OneDrive\Documents\Ramalan\sandbox_v46"

Write-Host "`n=== STEP 1: OCR (V4.6 FINAL schema, ~31 photos) ===" -ForegroundColor Cyan
python engines\ocr.py $photos $sid --force
if ($LASTEXITCODE -ne 0) { Write-Error "OCR step gagal"; exit 1 }

Write-Host "`n=== STEP 2: Build subject.json ===" -ForegroundColor Cyan
# OCR akan extract identity dari chart utama. Kalau missing, override via flags:
#   --name "X" --hanzi "X" --gender Pria/Wanita --date YYYY-MM-DD --time HH:MM
python engines\build_from_ocr.py $sid
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build gagal — kemungkinan ada field wajib hilang. Cek error msg di atas." -ForegroundColor Yellow
    Write-Host "Kalau identity missing, run ulang dengan flags:" -ForegroundColor Yellow
    Write-Host "  python engines\build_from_ocr.py $sid --name `"NAME`" --hanzi 漢字 --gender Pria --date 1980-01-01 --time 08:00" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n=== STEP 3: Render PDF ===" -ForegroundColor Cyan
python build_pdf.py $sid
if ($LASTEXITCODE -ne 0) { Write-Error "PDF render gagal"; exit 1 }

Write-Host "`n=== DONE ===" -ForegroundColor Green
Write-Host "PDF output: lihat path di log STEP 3 (biasanya #result\{date}\... atau _pdf_out\)"
