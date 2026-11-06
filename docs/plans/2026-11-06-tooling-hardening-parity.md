# Tooling Hardening & Parity Implementation Plan

> **For Claude / Antigravity:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Achieve 100% parity across AI_Flow installation, validation, and multi-provider execution tooling while ensuring full 14-skill coverage in IDE rules.

**Architecture:** Update installer scripts (PowerShell and Bash) to dynamically count and install all 14 skills into standard agent locations; enhance `validate.ps1` to mirror `validate.js` strict checks; extend `run.py` with native Anthropic Claude Messages API execution and interactive mode; update `.cursor/rules/ai-flow.mdc` to document all 14 skills across 3 lifecycle phases; normalize workspace diffs.

**Tech Stack:** PowerShell, Bash, Python 3 (`requests`, `dotenv`), Node.js, Markdown.

---

### Task 1: Workspace Normalization & Git Tree Cleanup

**Files:**
- Modify: `gemini.md`

**Step 1: Check diff and restore trailing whitespace**
Run: `git checkout -- gemini.md`

**Step 2: Verify git status is clean**
Run: `git status`
Expected: `nothing to commit, working tree clean` (except untracked plans/docs)

---

### Task 2: Installer Scripts Parity & Dynamic Counting

**Files:**
- Modify: `scripts/install.ps1:58`
- Modify: `scripts/install.sh:15-40`

**Step 1: Update `scripts/install.ps1`**
Modify completion message to use dynamic count:
```powershell
$skillDirs = Get-ChildItem -Path $SourceSkills -Directory
$totalCount = $skillDirs.Count
Write-Host "`nInstallation complete! All $totalCount skills are now available to your AI agents." -ForegroundColor Yellow
```

**Step 2: Update `scripts/install.sh`**
Add Antigravity destination and dynamic count:
```bash
DESTINATIONS=(
    "$HOME_DIR/.agents/skills"
    "$HOME_DIR/.gemini/antigravity/skills"
    "$HOME_DIR/.claude/skills"
)
```
And:
```bash
TOTAL_SKILLS=$(find "$SOURCE_SKILLS" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
echo ""
echo "Installation complete! All ${TOTAL_SKILLS} skills are now available to your AI agents."
```

**Step 3: Test execution**
Run: `powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Target antigravity`
Expected: Output showing 14 skills installed and message "All 14 skills are now available to your AI agents."

**Step 4: Commit**
```bash
git add scripts/install.ps1 scripts/install.sh
git commit -m "fix(scripts): dynamically count skills in installers and add Antigravity path to Bash installer"
```

---

### Task 3: Validator Parity (`scripts/validate.ps1`)

**Files:**
- Modify: `scripts/validate.ps1`

**Step 1: Implement strict spec checks in `scripts/validate.ps1`**
Update `scripts/validate.ps1` to mirror `scripts/validate.js`:
- Check description starts with `Use when\b` and `$desc.Length -le 500`.
- Check skill name matches directory name and regex `^[a-z0-9-]+$`.
- Check for `## Overview`, `## When to Use`, and `## (Instructions|The Two-Phase Contract)`.
- Exit with code 1 on failure.

**Step 2: Run both validators to verify identical results**
Run: `node scripts/validate.js`
Expected: All 14 skills passed.
Run: `powershell -ExecutionPolicy Bypass -File scripts/validate.ps1`
Expected: `Completed: 14 passed, 0 failed.`

**Step 3: Commit**
```bash
git add scripts/validate.ps1
git commit -m "feat(validator): bring PowerShell validator into full parity with validate.js"
```

---

### Task 4: Anthropic Claude Integration in CLI Runner

**Files:**
- Modify: `scripts/run.py`
- Modify: `.env.example`
- Modify: `README.md`

**Step 1: Add Anthropic provider and caller to `scripts/run.py`**
- Register `anthropic` in `PROVIDERS`:
  ```python
  "anthropic": {
      "env_key": "ANTHROPIC_API_KEY",
      "name": "Anthropic Claude",
  },
  ```
- Implement `call_anthropic()` targeting `https://api.anthropic.com/v1/messages` with `anthropic-version: 2023-06-01` and default model `claude-3-7-sonnet-latest`.
- Update `CALLERS["anthropic"] = call_anthropic`.
- Handle Anthropic multi-turn messages in `--interactive` mode.
- Update `detect_provider()` to check `ANTHROPIC_API_KEY`.

**Step 2: Update `.env.example`**
Add:
```env
# Anthropic Claude API Key (Optional)
# Get yours at: https://console.anthropic.com/
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Step 3: Update `README.md`**
Add Claude CLI runner example:
```bash
python scripts/run.py --skill prd-generator --input "A crypto portfolio tracker" --provider anthropic
```

**Step 4: Verify CLI functionality**
Run: `python scripts/run.py --help`
Expected: `anthropic` listed in `--provider` choices.
Run: `python scripts/run.py --list`
Expected: Output showing 14 skills.

**Step 5: Commit**
```bash
git add scripts/run.py .env.example README.md
git commit -m "feat(runner): add Anthropic Claude provider to CLI auto-writer"
```

---

### Task 5: Cursor Rules Full 14-Skill Coverage

**Files:**
- Modify: `.cursor/rules/ai-flow.mdc`

**Step 1: Update `.cursor/rules/ai-flow.mdc`**
Map all 14 skills organized by phase:
- Phase 1: `prd-generator`, `trd-generator`, `app-flow`, `uiux-design-brief`, `backend-schema`, `system-architecture`, `implementation-plan`.
- Phase 2: `task-to-skill`, `playwright-e2e-testing`, `systematic-debugging`.
- Phase 3: `security-gap-audit`, `dead-code-cleanup`, `rigorous-code-review`, `clean-git-commits`.

**Step 2: Verify rule content**
Inspect file to confirm formatting and paths.

**Step 3: Commit**
```bash
git add .cursor/rules/ai-flow.mdc
git commit -m "docs(cursor): expand workspace rules to cover all 14 lifecycle skills"
```

---

### Task 6: Final Verification & Git Cleanliness

**Step 1: Run full test suite**
- `node scripts/validate.js`
- `powershell -ExecutionPolicy Bypass -File scripts/validate.ps1`
- `python scripts/run.py --list`

**Step 2: Verify clean working directory**
Run: `git status`
Expected: Clean working tree.
