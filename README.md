# 🚀 AI_Flow

> **A 30-Skill, 60-Agent Autonomous Dual-Agent Ecosystem for Solo Founders, Full-Stack Engineers & Creators.**

[![Validate Skills](https://github.com/Syed-afridi-7/AI_Flow/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/Syed-afridi-7/AI_Flow/actions/workflows/validate-skills.yml)
[![Agent Skills Specification](https://img.shields.io/badge/Agent_Skills-Open_Standard-8A2BE2?style=for-the-badge&logo=anthropic)](https://agentskills.io)
[![Antigravity](https://img.shields.io/badge/Antigravity-Compatible-4285F4?style=for-the-badge&logo=google)](https://deepmind.google)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Supported-D97706?style=for-the-badge&logo=anthropic)](https://claude.ai)
[![Cursor](https://img.shields.io/badge/Cursor-Rules%20Included-000000?style=for-the-badge&logo=cursor)](https://cursor.com)
[![GitHub Copilot](https://img.shields.io/badge/Copilot-Instructions-black?style=for-the-badge&logo=githubcopilot)](https://github.com/features/copilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

## 📌 Overview

**AI_Flow** transforms solo software engineering, freelance operations, and content creation into an autonomous, startup-caliber foundry. Compliant with the [Agent Skills Open Specification](https://agentskills.io), it equips AI coding agents (**Google Antigravity**, **Claude Code**, **Cursor**, **GitHub Copilot**, **Windsurf**, and **Codex**) with **30 specialized skills** and **60 dual-agent personas** (Generator &harr; Validator peer review loops).

It runs natively as a local Windows background daemon with automatic email triage, file drop queues, and integrated social growth automation (Instagram reels and devlog repurposing).

---

## 🔄 The 8-Phase Autonomous Lifecycle (30 Skills, 60 Personas)

```mermaid
flowchart TD
    subgraph Phase 1: Product & Architecture
        A["1. prd-generator"] --> B["2. trd-generator"]
        B --> C["3. app-flow"]
        C --> D["4. uiux-design-brief"]
        D --> E["5. backend-schema"]
        E --> F["6. system-architecture"]
        F --> G["7. implementation-plan"]
    end

    subgraph Phase 2: Execution & Quality
        G --> H["8. task-to-skill"]
        H --> I["9. playwright-e2e-testing"]
        I --> J["10. systematic-debugging"]
    end

    subgraph Phase 3: Auditing & Release
        J --> K["11. security-gap-audit"]
        K --> L["12. dead-code-cleanup"]
        L --> M["13. rigorous-code-review"]
        M --> N["14. clean-git-commits"]
    end

    subgraph Phase 4: Design Systems & Frontend
        N --> O["15. design-system-tokens"]
        O --> P["16. landing-page-converter"]
        P --> Q["17. accessibility-wcag-audit"]
    end

    subgraph Phase 5: API, Database & Performance
        Q --> R["18. api-contract-generator"]
        R --> S["19. db-migration-optimizer"]
        S --> T["20. performance-profiling"]
    end

    subgraph Phase 6: DevOps, CI/CD & FinOps
        T --> U["21. devops-docker-deploy"]
        U --> V["22. ci-cd-pipeline-builder"]
        V --> W["23. finops-token-optimizer"]
    end

    subgraph Phase 7: Freelance & Client Business Operations
        W --> X["24. freelance-client-onboarding"]
        X --> Y["25. email-inbox-triage"]
        Y --> Z["26. invoice-billing-tracker"]
    end

    subgraph Phase 8: Social Growth & Founder OS
        Z --> AA["27. insta-reel-creator"]
        AA --> AB["28. seo-content-strategist"]
        AB --> AC["29. social-copy-repurposer"]
        AC --> AD["30. executive-time-ledger"]
    end
```

---

## 🛡️ Autonomous Dual-Agent Architecture

Every skill domain in `skills/` houses an `agents/` directory pairing two complementary personas:
1. **Generator (Persona A):** The architect, strategist, or builder producing the initial draft.
2. **Validator (Persona B):** The adversarial auditor evaluating the draft against an objective 100-point rubric.
3. **Self-Correcting Loop:** If score < 85, the Generator receives specific blockers and self-corrects (capped at 2 iterations to protect token budgets).

```bash
# Run any skill in autonomous dual-agent peer review mode:
python scripts/run.py --skill design-system-tokens --input "Dark mode SaaS tokens" --mode dual
```

---

## ⚡ Ways to Use AI_Flow

### 1. Autonomous Background Daemon & Email Triage (Windows)
AI_Flow runs as an autonomous background service at system login:
- Automatically triages client emails via IMAP (pure read & draft mode; never sends without approval).
- Watches `data/queue/inbox/` for dropped tasks and executes skills automatically.
- Schedules daily Instagram reel & devlog generation.

```powershell
# Manage the Windows background service
.\scripts\daemon-service.ps1 -Action Install   # Registers on-login task
.\scripts\daemon-service.ps1 -Action Status    # Inspects service & memory (<35MB)
.\scripts\daemon-service.ps1 -Action Stop      # Stops background daemon
```

---

### 2. Standalone Auto-Writer CLI
Run any skill directly from the terminal with **Gemini**, **Anthropic**, **OpenAI**, or **Grok**:

```bash
# Fast 1-turn single mode
python scripts/run.py --skill prd-generator --input "A crypto portfolio tracker"

# Autonomous 3-turn dual-agent mode with scorecard
python scripts/run.py --skill security-gap-audit --input "Audit auth middleware" --mode dual --provider anthropic

# List all 30 skills and dual-agent status
python scripts/run.py --list
```

---

### 3. Native Agent Skills Installation
Install all 30 skills directly into your global agent environment:

```powershell
# Windows
.\scripts\install.ps1
```

```bash
# macOS / Linux
chmod +x ./scripts/install.sh && ./scripts/install.sh
```

---

## 🤖 Cross-Runtime Configuration Adapters

- **[SKILL.md](SKILL.md):** Unified master spec covering all modules for direct upload to Gemini or ChatGPT.
- **[AGENTS.md](AGENTS.md):** Universal agent instructions recognized by all modern agents.
- **[CLAUDE.md](CLAUDE.md):** Memory context and skill mappings for Claude Code.
- **[.cursor/rules/](.cursor/rules/ai-flow.mdc):** Cursor IDE workspace rules applying skills across editor sessions.
- **[.github/copilot-instructions.md](.github/copilot-instructions.md):** Repository instructions for GitHub Copilot.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
