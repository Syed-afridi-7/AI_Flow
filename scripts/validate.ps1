$skillsDir = Join-Path $PSScriptRoot "..\skills"
$skills = Get-ChildItem -Path $skillsDir -Directory
$passed = 0
$failed = 0

Write-Host "Validating skills in $skillsDir..." -ForegroundColor Cyan

foreach ($dir in $skills) {
    $file = Join-Path $dir.FullName "SKILL.md"
    if (-not (Test-Path $file)) {
        Write-Host "FAIL: $($dir.Name) missing SKILL.md" -ForegroundColor Red
        $failed++
        continue
    }

    $text = [System.IO.File]::ReadAllText($file)
    $hasFrontmatter = $text.StartsWith("---")
    $hasName = $text -match '(?m)^name:\s+' + [regex]::Escape($dir.Name) + '$'
    $hasDesc = $text -match '(?m)^description:\s+Use when\b'
    $hasOverview = $text -match '(?m)^## Overview\b'
    $hasWhen = $text -match '(?m)^## When to Use\b'

    if ($hasFrontmatter -and $hasName -and $hasDesc -and $hasOverview -and $hasWhen) {
        Write-Host "  [OK] $($dir.Name)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "  [FAIL] $($dir.Name) failed validation checks" -ForegroundColor Red
        $failed++
    }
}

Write-Host "Completed: $passed passed, $failed failed." -ForegroundColor $(if ($failed -eq 0) { 'Green' } else { 'Red' })
if ($failed -gt 0) { exit 1 }
