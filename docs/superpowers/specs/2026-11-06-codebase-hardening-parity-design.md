# Design Specification: AI_Flow Tooling Hardening & Parity

**Date:** 2026-11-06  
**Status:** Approved  
**Author:** Pair Programming Agent & Syed Afridi  

---

## 1. Overview & Goal

AI_Flow recently expanded from 10 to 14 standardized Agent Skills covering the full software engineering lifecycle. Following a comprehensive codebase audit, this design hardens the automation tooling, achieves 100% parity across Windows (PowerShell) and POSIX (Bash) runtimes, introduces native Anthropic Claude API execution to the CLI runner, aligns Cursor IDE rules to encompass all 14 skills, and synchronizes spec validation scripts.

---

## 2. Requirements & Scope

1. **Installer Parity & Dynamic Counting:**
   - Both `install.ps1` and `install.sh` must dynamically count skills in `skills/` instead of hardcoding outdated numbers.
   - `install.sh` must include the Google Antigravity destination path (`~/.gemini/antigravity/skills`) matching `install.ps1` and the documentation in `README.md`.
2. **Anthropic Claude Integration in CLI Runner:**
   - Add `anthropic` provider to `scripts/run.py` supporting Anthropic's Messages API (`/v1/messages`).
   - Default model: `claude-3-7-sonnet-latest` (with custom model override via `-m/--model`).
   - Support interactive multi-turn conversations (`--interactive`).
   - Update `.env.example` with `ANTHROPIC_API_KEY`.
   - Update `README.md` with CLI examples for Anthropic.
3. **Validator Parity:**
   - Enhance `scripts/validate.ps1` to mirror all checks in `scripts/validate.js`:
     - Frontmatter presence and delimiter.
     - Skill name matching directory and regex `^[a-z0-9-]+$`.
     - Description starting with `Use when...` and length `<= 500` characters.
     - Presence of `## Overview`, `## When to Use`, and `## (Instructions|The Two-Phase Contract)`.
4. **Cursor Rules Coverage:**
   - Update `.cursor/rules/ai-flow.mdc` to map all 14 skills organized by Phase 1, Phase 2, and Phase 3.
5. **Git Tree Cleanliness:**
   - Normalize whitespace in `gemini.md`.

---

## 3. Technical Architecture & Component Changes

### 3.1 Installer Scripts

#### `scripts/install.ps1`
- Query the `skills/` directory dynamically:
  ```powershell
  $skillDirs = Get-ChildItem -Path $SourceSkills -Directory
  $totalCount = $skillDirs.Count
  ```
- Output message:
  ```powershell
  Write-Host "`nInstallation complete! All $totalCount skills are now available to your AI agents." -ForegroundColor Yellow
  ```

#### `scripts/install.sh`
- Add Antigravity target directory:
  ```bash
  DESTINATIONS=(
      "$HOME_DIR/.agents/skills"
      "$HOME_DIR/.gemini/antigravity/skills"
      "$HOME_DIR/.claude/skills"
  )
  ```
- Compute total skills dynamically:
  ```bash
  TOTAL_SKILLS=$(find "$SOURCE_SKILLS" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
  echo "Installation complete! All ${TOTAL_SKILLS} skills are now available to your AI agents."
  ```

---

### 3.2 CLI Auto-Writer Runner (`scripts/run.py`)

#### Provider Configuration
```python
PROVIDERS = {
    "gemini": {
        "env_key": "GEMINI_API_KEY",
        "name": "Google Gemini",
    },
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "name": "Anthropic Claude",
    },
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "name": "OpenAI ChatGPT",
    },
    "grok": {
        "env_key": "GROK_API_KEY",
        "name": "xAI Grok",
    },
}
```

#### API Caller Implementation
```python
def call_anthropic(system_prompt: str, user_prompt: str, api_key: str, model: str = "claude-3-7-sonnet-latest") -> str:
    """Call the Anthropic Claude Messages API."""
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 8192,
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["content"][0]["text"]
    except (KeyError, IndexError):
        print(f"⚠️  Unexpected Anthropic response:\n{json.dumps(data, indent=2)}")
        sys.exit(1)
```

#### Interactive Multi-Turn Mode
In multi-turn interactive loops, transform message histories into Anthropic schema:
- Extract `system` content to top-level `system` payload parameter.
- Filter remaining messages into `messages: [{"role": "user"|"assistant", "content": ...}]`.

---

### 3.3 Validator Parity (`scripts/validate.ps1`)

Expand validation loop in `scripts/validate.ps1`:
```powershell
$hasFrontmatter = $text -match '^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$'
# Validate Name
$nameMatch = $text -match '(?m)^name:\s*([a-z0-9-]+)\s*$'
$nameMatchesDir = ($Matches -and $Matches[1] -eq $dir.Name)

# Validate Description
$descMatch = $text -match '(?m)^description:\s*([\s\S]*?)(?=\n[a-z0-9_-]+:|$)'
$descValid = $false
if ($descMatch) {
    $desc = $Matches[1] -replace '\r?\n\s*', ' '
    $descValid = ($desc -match '^Use when\b') -and ($desc.Length -le 500)
}

# Validate Sections
$hasOverview = $text -match '(?m)^##\s+Overview\b'
$hasWhen = $text -match '(?m)^##\s+When to Use\b'
$hasInstructions = $text -match '(?m)^##\s+(Instructions|The Two-Phase Contract)\b'
```

---

### 3.4 Cursor Workspace Rules (`.cursor/rules/ai-flow.mdc`)

Structure the rules file cleanly into all 3 engineering phases, citing canonical skill paths:
- **Phase 1: Product, Requirements & Architecture**
  - `skills/prd-generator/SKILL.md`
  - `skills/trd-generator/SKILL.md`
  - `skills/app-flow/SKILL.md`
  - `skills/uiux-design-brief/SKILL.md`
  - `skills/backend-schema/SKILL.md`
  - `skills/system-architecture/SKILL.md`
  - `skills/implementation-plan/SKILL.md`
- **Phase 2: Execution & Quality**
  - `skills/task-to-skill/SKILL.md`
  - `skills/playwright-e2e-testing/SKILL.md`
  - `skills/systematic-debugging/SKILL.md`
- **Phase 3: Auditing & Release**
  - `skills/security-gap-audit/SKILL.md`
  - `skills/dead-code-cleanup/SKILL.md`
  - `skills/rigorous-code-review/SKILL.md`
  - `skills/clean-git-commits/SKILL.md`

---

## 4. Verification Plan

1. **Node.js Validator:** Run `node scripts/validate.js` &rarr; All 14 skills pass.
2. **PowerShell Validator:** Run `powershell -File scripts/validate.ps1` &rarr; All 14 skills pass under new strict checks.
3. **CLI Runner Check:** Run `python scripts/run.py --list` &rarr; List all 14 skills, verify providers list displays Anthropic, Gemini, OpenAI, Grok.
4. **Installer Dry-Run / Test:** Run `scripts/install.ps1` with `-Symlink` or dry-run &rarr; verify count outputs 14.
5. **Git Status:** Verify clean working tree without untracked artifacts.
