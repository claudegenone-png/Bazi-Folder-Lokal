$src = "C:\Users\sukam\OneDrive\Documents\Ramalan\cache\hulili"
$files = @(
  "page_01_cover.html",
  "page_02_toc.html",
  "page_03_intro.html",
  "page_profile.html",
  "page_05_bazi_opener.html",
  "page_06_daymaster.html",
  "page_marriage.html",
  "page_08_xingqing.html",
  "page_09_family.html",
  "page_10_shensha.html",
  "page_11_caifu.html",
  "page_career.html",
  "page_yangzhai.html",
  "page_dayun.html",
  "page_15_ziwei_opener.html",
  "page_ziwei.html",
  "page_17_palace1.html",
  "page_18_palace2.html",
  "page_19_palace3.html",
  "page_20_kesimpulan.html",
  "page_synthesis.html",
  "page_22_glossary.html",
  "page_23_disclaimer.html"
)

$styles = ""
$bodies = ""
foreach ($f in $files) {
  $content = Get-Content "$src\$f" -Raw -Encoding UTF8
  if ($content -match '(?s)<style>(.*?)</style>') {
    $styles += "/* === $f === */`r`n" + $matches[1] + "`r`n"
  }
  if ($content -match '(?s)<body[^>]*>(.*?)</body>') {
    $bodies += $matches[1] + "`r`n"
  }
}

$master = @"
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Hu Li Li — Laporan Ramalan Lengkap</title>
<link rel="stylesheet" href="style.css">
<style>
$styles

/* PDF EXPORT — force page break per section */
@page { size: A4 portrait; margin: 0; }
body { background: white !important; margin: 0; padding: 0; }
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

$out = "$src\report_hulili_full.html"
[System.IO.File]::WriteAllText($out, $master, [System.Text.UTF8Encoding]::new($false))
Write-Output "Master HTML built: $out"
Write-Output ("Size: " + ((Get-Item $out).Length / 1KB).ToString("N1") + " KB")
