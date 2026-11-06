# AI_Flow Skill Validator
# Validates all skills in the skills/ directory against the Agent Skills Open Specification (agentskills.io).

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$skillsDir = Join-Path $repoRoot "skills"

if (-not (Test-Path $skillsDir)) {
    Write-Host "Error: skills directory not found at $skillsDir" -ForegroundColor Red
    exit 1
}

$entries = Get-ChildItem -Path $skillsDir -Directory
$skillDirs = $entries | ForEach-Object { $_.Name }

$errors = [System.Collections.Generic.List[string]]::new()
$passedCount = 0

Write-Host "Validating $($skillDirs.Count) skills against the Agent Skills specification...`n" -ForegroundColor Cyan

foreach ($dirName in $skillDirs) {
    $skillPath = Join-Path $skillsDir (Join-Path $dirName "SKILL.md")

    if (-not (Test-Path $skillPath)) {
        $errors.Add("[$dirName] Missing SKILL.md file.")
        continue
    }

    $content = [System.IO.File]::ReadAllText($skillPath, [System.Text.Encoding]::UTF8)
    $frontmatterMatch = [regex]::Match($content, '(?s)^---\r?\n(.*?)\r?\n---\r?\n(.*)$')

    if (-not $frontmatterMatch.Success) {
        $errors.Add("[$dirName] Missing or malformed YAML frontmatter (must be enclosed in '---').")
        continue
    }

    $frontmatter = $frontmatterMatch.Groups[1].Value
    $body = $frontmatterMatch.Groups[2].Value

    # Validate Name
    $nameMatch = [regex]::Match($frontmatter, '(?m)^name:\s*(.+)$')
    if (-not $nameMatch.Success) {
        $errors.Add("[$dirName] Missing 'name' field in frontmatter.")
    } else {
        $name = $nameMatch.Groups[1].Value.Trim()
        if ($name -cne $dirName) {
            $errors.Add("[$dirName] Frontmatter name '$name' does not match directory name '$dirName'.")
        }
        if (-not [regex]::IsMatch($name, '^[a-z0-9-]+$')) {
            $errors.Add("[$dirName] Skill name '$name' contains invalid characters (use only lowercase letters, numbers, and hyphens).")
        }
    }

    # Validate Description
    $descMatch = [regex]::Match($frontmatter, '(?m)^description:\s*([\s\S]*?)(?=\r?\n[a-z0-9_-]+:|$)')
    if (-not $descMatch.Success) {
        $errors.Add("[$dirName] Missing 'description' field in frontmatter.")
    } else {
        $desc = [regex]::Replace($descMatch.Groups[1].Value, '\r?\n\s*', ' ').Trim()
        if (-not [regex]::IsMatch($desc, '^Use when\b', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
            $preview = if ($desc.Length -gt 40) { $desc.Substring(0, 40) } else { $desc }
            $errors.Add("[$dirName] Description must start with 'Use when...'. Got: `"$preview...`"")
        }
        if ($desc.Length -gt 500) {
            $errors.Add("[$dirName] Description exceeds 500 characters ($($desc.Length) chars).")
        }
    }

    # Validate Required Sections
    if (-not [regex]::IsMatch($body, '##\s+Overview', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
        $errors.Add("[$dirName] Missing '## Overview' section in body.")
    }
    if (-not [regex]::IsMatch($body, '##\s+When to Use', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
        $errors.Add("[$dirName] Missing '## When to Use' section in body.")
    }
    if (-not [regex]::IsMatch($body, '##\s+(Instructions|The Two-Phase Contract)', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
        $errors.Add("[$dirName] Missing '## Instructions' or '## The Two-Phase Contract' section in body.")
    }

    $hasDirError = $false
    foreach ($err in $errors) {
        if ($err.StartsWith("[$dirName]")) {
            $hasDirError = $true
            break
        }
    }

    if (-not $hasDirError) {
        $passedCount++
        Write-Host "  " -NoNewline
        Write-Host ([char]0x2713) -ForegroundColor Green -NoNewline
        Write-Host " $dirName"
    }
}

Write-Host ""

if ($errors.Count -gt 0) {
    Write-Host "Validation failed with $($errors.Count) error(s):" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  " -NoNewline
        Write-Host ([char]0x2716) -ForegroundColor Red -NoNewline
        Write-Host " $err"
    }
    exit 1
} else {
    Write-Host "All $passedCount skills passed validation successfully!" -ForegroundColor Green
}
