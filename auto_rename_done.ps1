$root = "C:\Users\sukam\OneDrive\Documents\Ramalan\foto\#database"
$today = Get-Date -Format "yyyy-MM-dd"
$dayFolder = Join-Path $root $today
if (-not (Test-Path $dayFolder)) { return }

Get-ChildItem -Path $dayFolder -Directory | Where-Object { $_.Name -match '^\d{2}$' } | ForEach-Object {
    $hasFiles = @(Get-ChildItem -Path $_.FullName -File -Recurse -ErrorAction SilentlyContinue).Count
    if ($hasFiles -gt 0) {
        $newName = "$($_.Name)-done"
        $newPath = Join-Path $dayFolder $newName
        if (-not (Test-Path $newPath)) {
            Rename-Item -Path $_.FullName -NewName $newName
            Write-Host "Renamed $($_.Name) -> $newName ($hasFiles files)"
        }
    }
}
