$root = "C:\Users\sukam\OneDrive\Documents\Ramalan\foto\#database"
$today = Get-Date -Format "yyyy-MM-dd"
$dayFolder = Join-Path $root $today
New-Item -ItemType Directory -Path $dayFolder -Force | Out-Null
1..10 | ForEach-Object {
    $sub = Join-Path $dayFolder ("{0:D2}" -f $_)
    New-Item -ItemType Directory -Path $sub -Force | Out-Null
}
Write-Host "Created $dayFolder with 10 subfolders 01-10"
