# build_preview.ps1 — builds master HTML only (no PDF), for browser preview
$ErrorActionPreference = 'Stop'
$src    = "C:\Users\sukam\OneDrive\Documents\Ramalan\cache\linruyi"
$shared = "C:\Users\sukam\OneDrive\Documents\Ramalan\cache\_shared"

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
<title>Lin Ru Yi — Preview HTML</title>
<link rel="stylesheet" href="$cssUrl">
<style>
$styles

.ind-icon, .toc-row .ico, .pal-action .ico, .dc-item .ico, .xqc-item .ico {
  font-family: 'Segoe UI Emoji','Segoe UI Symbol','Inter',system-ui,sans-serif !important;
}
</style>
</head>
<body>
$bodies
</body>
</html>
"@

$masterFile = "$src\report_linruyi_preview.html"
[System.IO.File]::WriteAllText($masterFile, $master, [System.Text.UTF8Encoding]::new($false))
$mSize = [math]::Round((Get-Item $masterFile).Length / 1KB, 1)
Write-Host "Preview HTML: $masterFile ($mSize KB)" -ForegroundColor Green
Write-Host "Open di browser untuk review."
