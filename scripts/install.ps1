# AI_Flow - Universal Multi-Tool & Skills Installer for Windows (PowerShell)
# Supports Google Antigravity, OpenAI Codex, Anthropic Claude, Grok, OpenCode, Open Agents, and Cursor AI.

[CmdletBinding()]
param(
    [ValidateSet('all', 'antigravity', 'codex', 'grok', 'opencode', 'claude', 'agents', 'cursor')]
    [string]$Target = 'all',
    [switch]$Symlink,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SourceSkills = Join-Path $RepoRoot "skills"
$SourceEngine = Join-Path $RepoRoot "engine"

if (-not (Test-Path -LiteralPath $SourceSkills)) {
    Write-Error "Source skills directory not found at: $SourceSkills"
    exit 1
}

$HomeDir = [System.Environment]::GetFolderPath('UserProfile')
if (-not $HomeDir) {
    $HomeDir = $env:USERPROFILE
}
if (-not $HomeDir) {
    $HomeDir = $HOME
}

# --- Safe ReparsePoint / Directory / File Removal Helper ---
function Remove-SafePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($null -ne $item) {
        try {
            $item.Attributes = 'Normal'
        } catch {
            # Ignore attribute errors
        }

        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            try {
                $item.Delete()
            } catch {
                Remove-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
            }
        } elseif ($item.PSIsContainer) {
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            Remove-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
        }
    } elseif (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# --- Directory Linking or Copying Helper ---
function Install-DirectoryTarget {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [switch]$UseSymlink,
        [switch]$ForceOverwrite
    )

    $parentDir = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    if ((Test-Path -LiteralPath $Destination) -or (Get-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue)) {
        Remove-SafePath -Path $Destination
    }

    if ($UseSymlink) {
        # Prefer Junction on Windows (no administrator privileges required)
        try {
            New-Item -ItemType Junction -Path $Destination -Target $Source -Force -ErrorAction Stop | Out-Null
            return "Junction"
        } catch {
            # Fallback to SymbolicLink
            try {
                New-Item -ItemType SymbolicLink -Path $Destination -Target $Source -Force -ErrorAction Stop | Out-Null
                return "SymbolicLink"
            } catch {
                # Fallback to recursive Copy
                Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
                return "Copy (fallback)"
            }
        }
    } else {
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
        return "Copy"
    }
}

# --- File Linking or Copying Helper ---
function Install-FileTarget {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [switch]$UseSymlink,
        [switch]$ForceOverwrite
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        Write-Warning "Source file not found: $Source"
        return "NotFound"
    }

    $parentDir = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    if ((Test-Path -LiteralPath $Destination) -or (Get-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue)) {
        Remove-SafePath -Path $Destination
    }

    if ($UseSymlink) {
        # Prefer HardLink for files (same volume), then SymbolicLink, then Copy
        try {
            New-Item -ItemType HardLink -Path $Destination -Target $Source -Force -ErrorAction Stop | Out-Null
            return "HardLink"
        } catch {
            try {
                New-Item -ItemType SymbolicLink -Path $Destination -Target $Source -Force -ErrorAction Stop | Out-Null
                return "SymbolicLink"
            } catch {
                Copy-Item -LiteralPath $Source -Destination $Destination -Force
                return "Copy (fallback)"
            }
        }
    } else {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        return "Copy"
    }
}

# --- Skills Collection Installer Helper ---
function Install-SkillsCollection {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [switch]$UseSymlink,
        [switch]$ForceOverwrite
    )

    if (-not (Test-Path -LiteralPath $Destination)) {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }

    $skillDirs = Get-ChildItem -Path $Source -Directory
    $count = 0
    $sampleMethod = ""

    foreach ($dir in $skillDirs) {
        $skillName = $dir.Name
        $targetSkillPath = Join-Path $Destination $skillName
        $method = Install-DirectoryTarget -Source $dir.FullName -Destination $targetSkillPath -UseSymlink:$UseSymlink -ForceOverwrite:$ForceOverwrite
        if (-not $sampleMethod) {
            $sampleMethod = $method
        }
        $count++
    }

    return @{
        Count = $count
        Method = $sampleMethod
    }
}

# --- Execution Orchestrator ---
$TargetsToRun = @()
if ($Target -eq 'all') {
    $TargetsToRun = @('antigravity', 'codex', 'grok', 'opencode', 'claude', 'agents', 'cursor')
} else {
    $TargetsToRun = @($Target)
}

$linkModeText = "Copy"
if ($Symlink) {
    $linkModeText = "Symlink / Junction"
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "       AI_Flow Multi-Tool & Multi-CLI Universal Installer (Windows)     " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "[i] Source Repository: $RepoRoot" -ForegroundColor DarkGray
Write-Host "[i] Target Selection:  $Target" -ForegroundColor DarkGray
Write-Host "[i] Installation Mode: $linkModeText" -ForegroundColor DarkGray
Write-Host ""

foreach ($currentTarget in $TargetsToRun) {
    switch ($currentTarget) {
        'antigravity' {
            Write-Host "[*] Configuring Google Antigravity & Gemini CLI..." -ForegroundColor Cyan

            $antigravitySkillsDirs = @(
                (Join-Path $HomeDir ".gemini\antigravity\skills"),
                (Join-Path $HomeDir ".gemini\antigravity-cli\skills")
            )

            foreach ($skillsDir in $antigravitySkillsDirs) {
                Write-Host "  [i] Skills target: $skillsDir" -ForegroundColor DarkGray
                $result = Install-SkillsCollection -Source $SourceSkills -Destination $skillsDir -UseSymlink:$Symlink -ForceOverwrite:$Force
                $count = $result.Count
                $mode = $result.Method
                Write-Host "  [+] Installed $count skills to $skillsDir (Mode: $mode)" -ForegroundColor Green
            }

            $geminiPluginDir = Join-Path $HomeDir ".gemini\config\plugins\ai-flow"
            Write-Host "  [i] Plugin target: $geminiPluginDir" -ForegroundColor DarkGray
            if (-not (Test-Path -LiteralPath $geminiPluginDir)) {
                New-Item -ItemType Directory -Path $geminiPluginDir -Force | Out-Null
            }

            $extSrc = Join-Path $RepoRoot "gemini-extension.json"
            $extDst = Join-Path $geminiPluginDir "gemini-extension.json"
            Install-FileTarget -Source $extSrc -Destination $extDst -UseSymlink:$Symlink -ForceOverwrite:$Force | Out-Null

            $pluginJsonSrc = Join-Path $RepoRoot "plugin.json"
            $pluginJsonDst = Join-Path $geminiPluginDir "plugin.json"
            Install-FileTarget -Source $pluginJsonSrc -Destination $pluginJsonDst -UseSymlink:$Symlink -ForceOverwrite:$Force | Out-Null

            $geminiMdSrc = Join-Path $RepoRoot "GEMINI.md"
            if (-not (Test-Path -LiteralPath $geminiMdSrc)) {
                $geminiMdSrc = Join-Path $RepoRoot "gemini.md"
            }
            $geminiMdDst = Join-Path $geminiPluginDir "GEMINI.md"
            Install-FileTarget -Source $geminiMdSrc -Destination $geminiMdDst -UseSymlink:$Symlink -ForceOverwrite:$Force | Out-Null

            $pluginSkillsDst = Join-Path $geminiPluginDir "skills"
            $pluginEngineDst = Join-Path $geminiPluginDir "engine"
            $skillsMode = Install-DirectoryTarget -Source $SourceSkills -Destination $pluginSkillsDst -UseSymlink:$Symlink -ForceOverwrite:$Force
            $engineMode = Install-DirectoryTarget -Source $SourceEngine -Destination $pluginEngineDst -UseSymlink:$Symlink -ForceOverwrite:$Force

            Write-Host "  [+] Antigravity extension & plugin registered at $geminiPluginDir (Skills: $skillsMode, Engine: $engineMode)" -ForegroundColor Green
            Write-Host ""
        }

        'codex' {
            Write-Host "[*] Configuring OpenAI Codex CLI..." -ForegroundColor Cyan

            $codexSkillsDir = Join-Path $HomeDir ".codex\skills"
            Write-Host "  [i] Skills target: $codexSkillsDir" -ForegroundColor DarkGray
            $result = Install-SkillsCollection -Source $SourceSkills -Destination $codexSkillsDir -UseSymlink:$Symlink -ForceOverwrite:$Force
            $count = $result.Count
            $mode = $result.Method
            Write-Host "  [+] Installed $count skills to $codexSkillsDir (Mode: $mode)" -ForegroundColor Green

            $codexPluginDir = Join-Path $HomeDir ".codex\plugins\ai-flow"
            Write-Host "  [i] Plugin target: $codexPluginDir" -ForegroundColor DarkGray
            if (-not (Test-Path -LiteralPath $codexPluginDir)) {
                New-Item -ItemType Directory -Path $codexPluginDir -Force | Out-Null
            }

            $codexManifestSrc = Join-Path $RepoRoot ".codex-plugin\plugin.json"
            if (Test-Path -LiteralPath $codexManifestSrc) {
                Install-FileTarget -Source $codexManifestSrc -Destination (Join-Path $codexPluginDir "plugin.json") -UseSymlink:$Symlink -ForceOverwrite:$Force | Out-Null
                $codexSubdir = Join-Path $codexPluginDir ".codex-plugin"
                if (-not (Test-Path -LiteralPath $codexSubdir)) {
                    New-Item -ItemType Directory -Path $codexSubdir -Force | Out-Null
                }
                Install-FileTarget -Source $codexManifestSrc -Destination (Join-Path $codexSubdir "plugin.json") -UseSymlink:$Symlink -ForceOverwrite:$Force | Out-Null
            }

            $codexSkillsDst = Join-Path $codexPluginDir "skills"
            $codexEngineDst = Join-Path $codexPluginDir "engine"
            $skillsMode = Install-DirectoryTarget -Source $SourceSkills -Destination $codexSkillsDst -UseSymlink:$Symlink -ForceOverwrite:$Force
            $engineMode = Install-DirectoryTarget -Source $SourceEngine -Destination $codexEngineDst -UseSymlink:$Symlink -ForceOverwrite:$Force

            Write-Host "  [+] Codex plugin registered at $codexPluginDir (Skills: $skillsMode, Engine: $engineMode)" -ForegroundColor Green
            Write-Host ""
        }

        'grok' {
            Write-Host "[*] Configuring Grok CLI..." -ForegroundColor Cyan

            $grokPluginDir = Join-Path $HomeDir ".grok\installed-plugins\ai-flow"
            Write-Host "  [i] Plugin target: $grokPluginDir" -ForegroundColor DarkGray
            if (-not (Test-Path -LiteralPath $grokPluginDir)) {
                New-Item -ItemType Directory -Path $grokPluginDir -Force | Out-Null
            }

            $grokSkillsDst = Join-Path $grokPluginDir "skills"
            $skillsMode = Install-DirectoryTarget -Source $SourceSkills -Destination $grokSkillsDst -UseSymlink:$Symlink -ForceOverwrite:$Force

            $pluginJsonSrc = Join-Path $RepoRoot "plugin.json"
            $pluginJsonDst = Join-Path $grokPluginDir "plugin.json"
            Install-FileTarget -Source $pluginJsonSrc -Destination $pluginJsonDst -UseSymlink:$Symlink -ForceOverwrite:$Force | Out-Null

            $agentsMdSrc = Join-Path $RepoRoot "AGENTS.md"
            $agentsMdDst = Join-Path $grokPluginDir "AGENTS.md"
            Install-FileTarget -Source $agentsMdSrc -Destination $agentsMdDst -UseSymlink:$Symlink -ForceOverwrite:$Force | Out-Null

            Write-Host "  [+] Grok plugin registered at $grokPluginDir (Skills: $skillsMode)" -ForegroundColor Green
            Write-Host ""
        }

        'opencode' {
            Write-Host "[*] Configuring OpenCode Interpreter..." -ForegroundColor Cyan

            $opencodeSkillsDir = Join-Path $HomeDir ".config\opencode\skills"
            Write-Host "  [i] Skills target: $opencodeSkillsDir" -ForegroundColor DarkGray
            $result = Install-SkillsCollection -Source $SourceSkills -Destination $opencodeSkillsDir -UseSymlink:$Symlink -ForceOverwrite:$Force
            $count = $result.Count
            $mode = $result.Method
            Write-Host "  [+] Installed $count skills to $opencodeSkillsDir (Mode: $mode)" -ForegroundColor Green

            $opencodePluginDir = Join-Path $HomeDir ".config\opencode\plugins"
            if (-not (Test-Path -LiteralPath $opencodePluginDir)) {
                New-Item -ItemType Directory -Path $opencodePluginDir -Force | Out-Null
            }
            $opencodePluginScriptDst = Join-Path $opencodePluginDir "ai-flow.js"
            $opencodePluginScriptSrc = Join-Path $RepoRoot ".opencode\plugins\ai-flow.js"

            if (Test-Path -LiteralPath $opencodePluginScriptSrc) {
                $scriptMode = Install-FileTarget -Source $opencodePluginScriptSrc -Destination $opencodePluginScriptDst -UseSymlink:$Symlink -ForceOverwrite:$Force
                Write-Host "  [+] OpenCode plugin script registered at $opencodePluginScriptDst (Mode: $scriptMode)" -ForegroundColor Green
            }
            Write-Host ""
        }

        'claude' {
            Write-Host "[*] Configuring Anthropic Claude Code..." -ForegroundColor Cyan

            $claudeSkillsDir = Join-Path $HomeDir ".claude\skills"
            Write-Host "  [i] Skills target: $claudeSkillsDir" -ForegroundColor DarkGray
            $result = Install-SkillsCollection -Source $SourceSkills -Destination $claudeSkillsDir -UseSymlink:$Symlink -ForceOverwrite:$Force
            $count = $result.Count
            $mode = $result.Method
            Write-Host "  [+] Installed $count skills to $claudeSkillsDir (Mode: $mode)" -ForegroundColor Green
            Write-Host ""
        }

        'agents' {
            Write-Host "[*] Configuring Open Agents Standard..." -ForegroundColor Cyan

            $agentsSkillsDir = Join-Path $HomeDir ".agents\skills"
            Write-Host "  [i] Skills target: $agentsSkillsDir" -ForegroundColor DarkGray
            $result = Install-SkillsCollection -Source $SourceSkills -Destination $agentsSkillsDir -UseSymlink:$Symlink -ForceOverwrite:$Force
            $count = $result.Count
            $mode = $result.Method
            Write-Host "  [+] Installed $count skills to $agentsSkillsDir (Mode: $mode)" -ForegroundColor Green
            Write-Host ""
        }

        'cursor' {
            Write-Host "[*] Configuring Cursor AI..." -ForegroundColor Cyan

            $cursorSkillsDir = Join-Path $HomeDir ".cursor\skills"
            Write-Host "  [i] Skills target: $cursorSkillsDir" -ForegroundColor DarkGray
            $result = Install-SkillsCollection -Source $SourceSkills -Destination $cursorSkillsDir -UseSymlink:$Symlink -ForceOverwrite:$Force
            $count = $result.Count
            $mode = $result.Method
            Write-Host "  [+] Installed $count skills to $cursorSkillsDir (Mode: $mode)" -ForegroundColor Green

            $srcCursorRule = Join-Path $RepoRoot ".cursor\rules\ai-flow.mdc"
            if (Test-Path -LiteralPath $srcCursorRule) {
                $cursorRulesDir = Join-Path $HomeDir ".cursor\rules"
                if (-not (Test-Path -LiteralPath $cursorRulesDir)) {
                    New-Item -ItemType Directory -Path $cursorRulesDir -Force | Out-Null
                }
                $cursorRuleDst = Join-Path $cursorRulesDir "ai-flow.mdc"
                Install-FileTarget -Source $srcCursorRule -Destination $cursorRuleDst -UseSymlink:$Symlink -ForceOverwrite:$Force | Out-Null
                Write-Host "  [+] Cursor rules installed to $cursorRuleDst" -ForegroundColor Green
            }
            Write-Host ""
        }
    }
}

$skillDirs = Get-ChildItem -Path $SourceSkills -Directory
$totalSkillsCount = $skillDirs.Count

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "              AI_Flow Multi-CLI Installation Complete                   " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "[+] Total AI_Flow Skills Available: $totalSkillsCount" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps & Agent Activation:" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

if (($Target -eq 'all') -or ($Target -eq 'antigravity')) {
    Write-Host "[i] Antigravity:" -ForegroundColor Cyan
    Write-Host "    ai-flow plugin registered at ~/.gemini/config/plugins/ai-flow" -ForegroundColor White
    Write-Host "    Resolved Path: $HomeDir\.gemini\config\plugins\ai-flow" -ForegroundColor DarkGray
    Write-Host ""
}

if (($Target -eq 'all') -or ($Target -eq 'codex')) {
    Write-Host "[i] Codex:" -ForegroundColor Cyan
    Write-Host "    ai-flow plugin registered at ~/.codex/plugins/ai-flow" -ForegroundColor White
    Write-Host "    Resolved Path: $HomeDir\.codex\plugins\ai-flow" -ForegroundColor DarkGray
    Write-Host ""
}

if (($Target -eq 'all') -or ($Target -eq 'opencode')) {
    Write-Host "[i] OpenCode:" -ForegroundColor Cyan
    Write-Host "    ai-flow plugin registered at ~/.config/opencode/plugins/ai-flow.js" -ForegroundColor White
    Write-Host "    Resolved Path: $HomeDir\.config\opencode\plugins\ai-flow.js" -ForegroundColor DarkGray
    Write-Host ""
}

if (($Target -eq 'all') -or ($Target -eq 'claude')) {
    Write-Host "[i] Claude:" -ForegroundColor Cyan
    Write-Host "    claude plugin marketplace add Syed-afridi-7/AI_Flow" -ForegroundColor White
    Write-Host "    Resolved Path: $HomeDir\.claude\skills" -ForegroundColor DarkGray
    Write-Host ""
}

if (($Target -eq 'all') -or ($Target -eq 'grok')) {
    Write-Host "[i] Grok:" -ForegroundColor Cyan
    Write-Host "    ai-flow plugin registered at ~/.grok/installed-plugins/ai-flow" -ForegroundColor White
    Write-Host "    Resolved Path: $HomeDir\.grok\installed-plugins\ai-flow" -ForegroundColor DarkGray
    Write-Host ""
}

if (($Target -eq 'all') -or ($Target -eq 'agents')) {
    Write-Host "[i] Agents:" -ForegroundColor Cyan
    Write-Host "    Skills installed at: $HomeDir\.agents\skills" -ForegroundColor DarkGray
    Write-Host ""
}

if (($Target -eq 'all') -or ($Target -eq 'cursor')) {
    Write-Host "[i] Cursor:" -ForegroundColor Cyan
    Write-Host "    Skills installed at: $HomeDir\.cursor\skills" -ForegroundColor DarkGray
    Write-Host ""
}

Write-Host "[i] Ollama:" -ForegroundColor Cyan
Write-Host "    ollama create ai-flow -f Modelfile" -ForegroundColor White
Write-Host "    Run locally: python scripts/run.py --provider ollama --skill prd-generator --input `"Build user auth`"" -ForegroundColor DarkGray
Write-Host "========================================================================" -ForegroundColor Cyan
