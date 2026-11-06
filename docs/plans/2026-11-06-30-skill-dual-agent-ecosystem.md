# 30-Skill Dual-Agent Autonomous Ecosystem Implementation Plan

> **For Claude / Antigravity:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand AI_Flow from 14 to 30 standardized Agent Skills, deploy a Dual-Agent Architecture (60 specialized agent personas), integrate the `E:\Insta_Reel` pipeline, and construct an autonomous local Windows background daemon with email triage and task queueing.

**Architecture:** Scaffold 16 new skill domains compliant with `agentskills.io`; author `generator.md` and `validator.md` personas for all 30 skills; upgrade `scripts/run.py` to support `--mode dual` with model tiering (fast generator + reasoning auditor) and prefix caching; modularize `E:\Insta_Reel` into `skills/insta-reel-creator/lib/`; implement `scripts/daemon.py` and `scripts/daemon-service.ps1` for Windows startup execution; validate all 30 skills across Node and PowerShell suites.

**Tech Stack:** Python 3 (`requests`, `python-dotenv`, `sqlite3`, `imaplib`), PowerShell 7/5.1, Node.js, Markdown.

---

## Phase 1: Foundation & The 16 New Skills Scaffolding

### Task 1: Scaffold Domain A (Design Systems & Frontend)
**Files:**
- Create: `skills/design-system-tokens/SKILL.md`
- Create: `skills/design-system-tokens/agents/generator.md`
- Create: `skills/design-system-tokens/agents/validator.md`
- Create: `skills/landing-page-converter/SKILL.md`
- Create: `skills/landing-page-converter/agents/generator.md`
- Create: `skills/landing-page-converter/agents/validator.md`
- Create: `skills/accessibility-wcag-audit/SKILL.md`
- Create: `skills/accessibility-wcag-audit/agents/generator.md`
- Create: `skills/accessibility-wcag-audit/agents/validator.md`

**Step 1:** Author each `SKILL.md` adhering to the spec (`name`, `description: Use when... <= 500 chars`, `## Overview`, `## When to Use`, `## Instructions`).
**Step 2:** Author `generator.md` (role, constraints, output structure) and `validator.md` (audit rubric, scorecard schema) for each.
**Step 3:** Run `node scripts/validate.js` to ensure all 3 new skills pass.
**Step 4:** Commit: `feat(skills): add design-system-tokens, landing-page-converter, and accessibility-wcag-audit skills`

---

### Task 2: Scaffold Domain B (API, Database & Performance)
**Files:**
- Create: `skills/api-contract-generator/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)
- Create: `skills/db-migration-optimizer/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)
- Create: `skills/performance-profiling/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)

**Step 1:** Author each `SKILL.md` and dual agent personas.
**Step 2:** Run `node scripts/validate.js` to ensure skills pass.
**Step 3:** Commit: `feat(skills): add api-contract-generator, db-migration-optimizer, and performance-profiling skills`

---

### Task 3: Scaffold Domain C (DevOps, CI/CD & FinOps)
**Files:**
- Create: `skills/devops-docker-deploy/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)
- Create: `skills/ci-cd-pipeline-builder/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)
- Create: `skills/finops-token-optimizer/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)

**Step 1:** Author each `SKILL.md` and dual agent personas.
**Step 2:** Run `node scripts/validate.js` to ensure skills pass.
**Step 3:** Commit: `feat(skills): add devops-docker-deploy, ci-cd-pipeline-builder, and finops-token-optimizer skills`

---

### Task 4: Scaffold Domain D (Freelance & Client Business Operations)
**Files:**
- Create: `skills/freelance-client-onboarding/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)
- Create: `skills/email-inbox-triage/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)
- Create: `skills/invoice-billing-tracker/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)

**Step 1:** Author each `SKILL.md` and dual agent personas.
**Step 2:** Run `node scripts/validate.js` to ensure skills pass.
**Step 3:** Commit: `feat(skills): add freelance-client-onboarding, email-inbox-triage, and invoice-billing-tracker skills`

---

### Task 5: Scaffold Domain E & F (Growth, Content & Founder OS)
**Files:**
- Create: `skills/insta-reel-creator/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)
- Create: `skills/seo-content-strategist/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)
- Create: `skills/social-copy-repurposer/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)
- Create: `skills/executive-time-ledger/SKILL.md` (+ `agents/generator.md`, `agents/validator.md`)

**Step 1:** Author each `SKILL.md` and dual agent personas.
**Step 2:** Run `node scripts/validate.js` to verify all 30 skills pass.
**Step 3:** Commit: `feat(skills): add insta-reel-creator, seo-content-strategist, social-copy-repurposer, and executive-time-ledger skills`

---

### Task 6: Scaffold Dual-Agent Personas for the Existing 14 Skills
**Files:**
- Create: `skills/<existing-14-skills>/agents/generator.md`
- Create: `skills/<existing-14-skills>/agents/validator.md`

**Step 1:** Generate Generator and Validator persona definitions for skills 1 through 14 matching the master matrix.
**Step 2:** Commit: `feat(agents): add dual-agent generator and validator personas for existing 14 skills`

---

## Phase 2: Dual-Agent Execution Engine & Token Optimizer

### Task 7: Dual-Agent Execution Engine in `scripts/run.py`
**Files:**
- Modify: `scripts/run.py`

**Step 1:** Add `--mode {single,dual}` CLI argument (default: `single`).
**Step 2:** In dual mode:
- Load `skills/<skill>/agents/generator.md` and `skills/<skill>/agents/validator.md`.
- Turn 1: Call generator with user input &rarr; receive `Draft 1`.
- Turn 2: Call validator with `Draft 1` &rarr; receive JSON evaluation (`score`, `verdict`, `blockers`).
- Turn 3 (Conditional): If `verdict == "REVISE"`, call generator with blockers &rarr; receive `Draft 2`, then final validator check.
**Step 3:** Test dual mode on a sample skill:
`python scripts/run.py --skill prd-generator --input "Test app" --mode dual`
**Step 4:** Commit: `feat(runner): implement autonomous dual-agent feedback loop in scripts/run.py`

---

### Task 8: Model Tiering & Prefix Caching in `scripts/run.py`
**Files:**
- Modify: `scripts/run.py`

**Step 1:** Add `--model-generator` and `--model-validator` arguments:
- Default Generator: Fast tier (`gemini-2.5-flash`, `gpt-4o-mini`).
- Default Validator: Reasoning tier (`claude-3-7-sonnet`, `gemini-2.5-pro`).
**Step 2:** Format system prompts with invariant static prefixes (>1024 tokens) to trigger provider prompt caching.
**Step 3:** Commit: `feat(runner): add model tiering and prompt caching optimization`

---

## Phase 3: Instagram Growth Engine Integration

### Task 9: Modularize `E:\Insta_Reel` into `skills/insta-reel-creator/lib/`
**Files:**
- Create: `skills/insta-reel-creator/lib/hookscore.py`
- Create: `skills/insta-reel-creator/lib/beats.py`
- Create: `skills/insta-reel-creator/lib/humanize.py`
- Create: `skills/insta-reel-creator/lib/memory.py`
- Create: `data/memory.db`

**Step 1:** Port hook scoring heuristics, 5-beat spoken timing structure, slop sanitizer, and SQLite topic memory from `E:\Insta_Reel`.
**Step 2:** Test execution of hookscore and beats headlessly with Python.
**Step 3:** Commit: `feat(insta-reel): modularize hookscore, beats, humanize, and SQLite topic memory into skill library`

---

## Phase 4: OS Background Daemon & Windows Startup Service

### Task 10: Implement `scripts/daemon.py`
**Files:**
- Create: `scripts/daemon.py`
- Create: `data/queue/inbox/.gitkeep`
- Create: `data/queue/processing/.gitkeep`
- Create: `data/queue/completed/.gitkeep`

**Step 1:** Implement heartbeat daemon loop:
- IMAP inbox check for client inquiries &rarr; runs `email-inbox-triage` skill in dual mode &rarr; writes draft to `output/email_drafts/`.
- File drop watcher: checks `data/queue/inbox/` for new tasks &rarr; moves to `processing/` &rarr; runs designated skill &rarr; saves output to `completed/`.
- Daily schedule watcher: triggers daily devlog and Instagram reel generation at scheduled time.
**Step 2:** Test daemon lifecycle in dry-run mode: `python scripts/daemon.py --dry-run`.
**Step 3:** Commit: `feat(daemon): implement autonomous local background daemon with email triage and task queue`

---

### Task 11: Windows Startup & Service Management Script
**Files:**
- Create: `scripts/daemon-service.ps1`
- Modify: `.env.example`

**Step 1:** Create `scripts/daemon-service.ps1` supporting:
- `-Action Install`: Registers Windows Task Scheduler task running at user logon.
- `-Action Status`: Displays PID, uptime, and memory usage.
- `-Action Stop`: Terminates running daemon process.
- `-Action Start`: Spawns daemon in background via `Start-Process pythonw`.
**Step 2:** Update `.env.example` with email IMAP configuration (`EMAIL_IMAP_SERVER`, `EMAIL_ACCOUNT`, `EMAIL_APP_PASSWORD`).
**Step 3:** Commit: `feat(daemon): add Windows startup service installer and management script`

---

## Phase 5: Verification, Cross-Runtime Sync & Final Documentation

### Task 12: Validate All 30 Skills across Node & PowerShell Suites
**Step 1:** Run `node scripts/validate.js` &rarr; Verify all 30 skills pass.
**Step 2:** Run `powershell -ExecutionPolicy Bypass -File scripts/validate.ps1` &rarr; Verify all 30 skills pass.
**Step 3:** Run `powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Target antigravity` &rarr; Verify installation of all 30 skills.

---

### Task 13: Documentation & Cross-Runtime Adapters Sync
**Files:**
- Modify: `README.md`
- Modify: `SKILL.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `gemini.md`
- Modify: `.cursor/rules/ai-flow.mdc`
- Modify: `.github/copilot-instructions.md`

**Step 1:** Update all root documentation files to map all 30 skills, the dual-agent architecture, and background daemon operations.
**Step 2:** Final commit: `docs: document complete 30-skill dual-agent autonomous ecosystem`
