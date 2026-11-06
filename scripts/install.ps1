# AI_Flow - Multi-Agent Skills Installer for Windows (PowerShell)
[CmdletBinding()]
param(
    [ValidateSet('all', 'agents', 'antigravity', 'claude', 'cursor')]
    [string]$Target = 'all',
    [switch]$Symlink
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SourceSkills = Join-Path $RepoRoot "skills"

if (-not (Test-Path $SourceSkills)) {
    Write-Error "Source skills directory not found at $SourceSkills"
    exit 1
}

$HomeDir = [System.Environment]::GetFolderPath('UserProfile')
$Destinations = @()

if ($Target -in @('all', 'agents')) {
    $Destinations += Join-Path $HomeDir ".agents\skills"
}
if ($Target -in @('all', 'antigravity')) {
    $Destinations += Join-Path $HomeDir ".gemini\antigravity\skills"
}
if ($Target -in @('all', 'claude')) {
    $Destinations += Join-Path $HomeDir ".claude\skills"
}

Write-Host "Installing AI_Flow skills from: $SourceSkills" -ForegroundColor Cyan

foreach ($dest in $Destinations) {
    if (-not (Test-Path $dest)) {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
        Write-Host "Created target directory: $dest" -ForegroundColor DarkGray
    }

    Get-ChildItem -Path $SourceSkills -Directory | ForEach-Object {
        $skillName = $_.Name
        $targetSkillPath = Join-Path $dest $skillName

        if (Test-Path $targetSkillPath) {
            Remove-Item -Recurse -Force $targetSkillPath
        }

        if ($Symlink) {
            New-Item -ItemType SymbolicLink -Path $targetSkillPath -Target $_.FullName -Force | Out-Null
            Write-Host "  [Symlink] $skillName -> $dest" -ForegroundColor Green
        } else {
            Copy-Item -Path $_.FullName -Destination $targetSkillPath -Recurse -Force
            Write-Host "  [Installed] $skillName -> $dest" -ForegroundColor Green
        }
    }
}

Write-Host "`nInstallation complete! All 10 skills are now available to your AI agents." -ForegroundColor Yellow

