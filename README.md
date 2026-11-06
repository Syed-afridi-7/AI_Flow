# 🚀 AI_Flow

> **A standardized, cross-runtime Agentic Skills suite & prompt framework for all modern AI coding agents.**

[![Validate Skills](https://github.com/Syed-afridi-7/AI_Flow/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/Syed-afridi-7/AI_Flow/actions/workflows/validate-skills.yml)
[![Agent Skills Specification](https://img.shields.io/badge/Agent_Skills-Open_Standard-8A2BE2?style=for-the-badge&logo=anthropic)](https://agentskills.io)
[![Antigravity](https://img.shields.io/badge/Antigravity-Compatible-4285F4?style=for-the-badge&logo=google)](https://deepmind.google)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Supported-D97706?style=for-the-badge&logo=anthropic)](https://claude.ai)
[![Cursor](https://img.shields.io/badge/Cursor-Rules%20Included-000000?style=for-the-badge&logo=cursor)](https://cursor.com)
[![GitHub Copilot](https://img.shields.io/badge/Copilot-Instructions-black?style=for-the-badge&logo=githubcopilot)](https://github.com/features/copilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

## 📌 Overview

**AI_Flow** transforms chaotic prompt interactions into disciplined, production-grade engineering workflows. Compliant with the [Agent Skills Open Specification](https://agentskills.io), it equips your AI pair programmers (**Google Antigravity**, **Claude Code**, **Cursor**, **GitHub Copilot**, **Windsurf**, and **Codex**) &mdash; or direct web chat interfaces (**Google Gemini**, **ChatGPT**, and **xAI Grok**) &mdash; with executable, self-contained skills covering every stage of the software lifecycle.

No hallucinated requirements. No premature fixes. No broken git commits.

---

## 🔄 The AI_Flow Lifecycle

```mermaid
flowchart TD
    subgraph Phase 1: Product, Design & Architecture
        A["1. prd-generator<br/><b>PRD: Requirements & Scope</b>"] --> B["2. trd-generator<br/><b>TRD: Technical Constraints & SLAs</b>"]
        B --> C["3. app-flow<br/><b>App Flow & State Transitions</b>"]
        C --> D["4. uiux-design-brief<br/><b>UI/UX Tokens & Component Library</b>"]
        D --> E["5. backend-schema<br/><b>Backend Schema, ERD & DDL</b>"]
        E --> F["6. system-architecture<br/><b>Topology & API Contracts</b>"]
        F --> G["7. implementation-plan<br/><b>Phased Engineering Roadmap</b>"]
    end

    subgraph Phase 2: Execution & Quality
        G --> H["8. task-to-skill<br/><b>Skill Modularization</b>"]
        H --> I["9. playwright-e2e-testing<br/><b>E2E Testing Suite</b>"]
        I --> J["10. systematic-debugging<br/><b>5-Step Root-Cause Analysis</b>"]
    end

    subgraph Phase 3: Auditing & Release
        J --> K["11. security-gap-audit<br/><b>Pre-Launch Threat Audit</b>"]
        K --> L["12. dead-code-cleanup<br/><b>Two-Phase Safe Pruning</b>"]
        L --> M["13. rigorous-code-review<br/><b>Blocker & Regression Review</b>"]
        M --> N["14. clean-git-commits<br/><b>Atomic Conventional Commits</b>"]
    end
```

---

## ⚡ 3 Ways to Use AI_Flow

### 1. Direct Web UI Upload (Gemini, ChatGPT, Grok)
- **Google Gemini:** Upload the repository folder or the single master [**`SKILL.md`**](SKILL.md) to Gemini (or inside a Gemini Gem). Gemini will recognize all 14 modules automatically!
- **ChatGPT Custom GPT:** Create a Custom GPT, upload [**`SKILL.md`**](SKILL.md) or the [`skills/`](skills/) folder into Knowledge, and paste [`AGENTS.md`](AGENTS.md) into Instructions.
- **xAI Grok:** Copy and paste the prompt of the module you want to run from root files (e.g., [`PRD.md`](PRD.md), [`TRD.md`](TRD.md), [`BackendSchema.md`](BackendSchema.md)).

---

### 2. Standalone Auto-Writer CLI (Generate Files Straight to Disk)
Don't want to use any agent CLIs? Run our standalone Python auto-writer that calls the **Gemini**, **OpenAI**, or **Grok** APIs directly and saves markdown documents directly to your drive:

```bash
# 1. Install dependencies
pip install requests python-dotenv

# 2. Configure your API keys in .env
cp .env.example .env

# 3. Run any skill and auto-save the output file
python scripts/run.py --skill prd-generator --input "A crypto portfolio tracker"
python scripts/run.py --skill trd-generator --input "Real-time trading system" --provider gemini
python scripts/run.py --skill app-flow --input "Multi-step onboarding flow" --provider openai
python scripts/run.py --skill backend-schema --input "SaaS billing & subscription models" --provider grok
python scripts/run.py --skill implementation-plan --input "MVP release plan" --provider gemini
```

---

### 3. Native Agent Skills Installation (Antigravity & Claude Code)
Install all 14 skills directly into your global agent environment with a single command:

#### Windows (PowerShell)
```powershell
.\scripts\install.ps1
```
*(Optionally pass `-Symlink` to create live development symlinks).*

#### macOS / Linux (Bash)
```bash
chmod +x ./scripts/install.sh && ./scripts/install.sh
```

This registers the skills with:
- **`~/.agents/skills/`** (Cross-runtime standard)
- **`~/.gemini/antigravity/skills/`** (Google Antigravity)
- **`~/.claude/skills/`** (Anthropic Claude Code)

---

## 📂 Skills Catalog & Reference

All 14 skills follow the official `skills/<skill-name>/SKILL.md` format, are unified in the root [**`SKILL.md`**](SKILL.md), and are paired with standalone root prompt templates:

| Skill | Canonical Spec | Standalone Prompt | Triggering Condition |
| :--- | :--- | :--- | :--- |
| **`prd-generator`** | [`skills/prd-generator/SKILL.md`](skills/prd-generator/SKILL.md) | [`PRD.md`](PRD.md) | Initiating a new product, defining scope, or translating an unformed idea into a structured specification before coding. |
| **`trd-generator`** | [`skills/trd-generator/SKILL.md`](skills/trd-generator/SKILL.md) | [`TRD.md`](TRD.md) | Translating product requirements into technical requirements, non-functional targets, latency/RPS budgets, and SLAs. |
| **`app-flow`** | [`skills/app-flow/SKILL.md`](skills/app-flow/SKILL.md) | [`AppFlow.md`](AppFlow.md) | Mapping user navigation journeys, screen-to-screen transitions, permission gates, and edge-case state machines. |
| **`uiux-design-brief`** | [`skills/uiux-design-brief/SKILL.md`](skills/uiux-design-brief/SKILL.md) | [`UIUX_Design.md`](UIUX_Design.md) | Translating requirements into UI/UX architecture, tokens, screen flows, or component contracts before frontend work. |
| **`backend-schema`** | [`skills/backend-schema/SKILL.md`](skills/backend-schema/SKILL.md) | [`BackendSchema.md`](BackendSchema.md) | Designing database schemas, Mermaid ERD, table DDL, keys, foreign key cascades, and high-performance composite indexes. |
| **`system-architecture`** | [`skills/system-architecture/SKILL.md`](skills/system-architecture/SKILL.md) | [`Architecture.md`](Architecture.md) | Architecting systems, selecting tech stacks, designing topology, or defining API contracts. |
| **`implementation-plan`** | [`skills/implementation-plan/SKILL.md`](skills/implementation-plan/SKILL.md) | [`ImplementationPlan.md`](ImplementationPlan.md) | Breaking down feature specifications into phased engineering implementation plans, dependencies, and test checkpoints. |
| **`task-to-skill`** | [`skills/task-to-skill/SKILL.md`](skills/task-to-skill/SKILL.md) | [`TaskToSkill.md`](TaskToSkill.md) | Turning a completed engineering task or workflow into a permanent, reusable Agent Skill. |
| **`playwright-e2e-testing`** | [`skills/playwright-e2e-testing/SKILL.md`](skills/playwright-e2e-testing/SKILL.md) | [`PlayWright.md`](PlayWright.md) | Configuring Playwright, mapping user journeys, or writing resilient browser tests. |
| **`systematic-debugging`** | [`skills/systematic-debugging/SKILL.md`](skills/systematic-debugging/SKILL.md) | [`Debug.md`](Debug.md) | Investigating bugs, runtime errors, or failing tests using a strict 5-step hypothesis and proof protocol. |
| **`security-gap-audit`** | [`skills/security-gap-audit/SKILL.md`](skills/security-gap-audit/SKILL.md) | [`SecGap.md`](SecGap.md) | Conducting pre-launch security reviews, vulnerability scans, threat modeling, or checking for secrets leaks. |
| **`dead-code-cleanup`** | [`skills/dead-code-cleanup/SKILL.md`](skills/dead-code-cleanup/SKILL.md) | [`DeadCode.md`](DeadCode.md) | Safely pruning unused files, obsolete dependencies, dead imports, or duplicate logic (Audit &rarr; Approve &rarr; Execute). |
| **`rigorous-code-review`** | [`skills/rigorous-code-review/SKILL.md`](skills/rigorous-code-review/SKILL.md) | [`CodeReview.md`](CodeReview.md) | Reviewing pull requests and code diffs for logic bugs, performance regressions, and contract breaks. |
| **`clean-git-commits`** | [`skills/clean-git-commits/SKILL.md`](skills/clean-git-commits/SKILL.md) | [`GIT.md`](GIT.md) | Splitting work into atomic commits formatted according to Conventional Commits. |

---

## 🤖 Cross-Runtime Configuration Adapters

This repository includes native configuration adapters out of the box:

- **[SKILL.md](SKILL.md):** Root master skill covering all 14 modules for direct upload to Gemini or agent runtimes.
- **[AGENTS.md](AGENTS.md):** Universal agent instructions recognized by all modern agents.
- **[CLAUDE.md](CLAUDE.md):** Memory context and skill mappings for Claude Code.
- **[.cursor/rules/](.cursor/rules/ai-flow.mdc):** Cursor IDE workspace rules applying skills during active editor sessions.
- **[.github/copilot-instructions.md](.github/copilot-instructions.md):** Repository-level instructions for GitHub Copilot Chat & Workspace.

---

## 💡 Core Philosophy

- **Two-Phase Enforcement:** High-risk tasks (debugging, dead code removal, security audits) enforce an **Audit / Verify First** stop before modifying production code.
- **Zero Hallucination:** Agents are mandated to ask clarifying questions rather than guessing ambiguous business logic.
- **Atomic Verifiability:** Every git commit must build, pass tests, and state the technical rationale behind the change.

---

## 🤝 Contributing

Contributions of new skills and improvements are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for skill authoring standards.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
