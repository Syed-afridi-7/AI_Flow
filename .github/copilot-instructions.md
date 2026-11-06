# GitHub Copilot Instructions

## Repository Overview
This repository provides **AI_Flow**, a standardized framework of 30 Agentic Skills and 60 dual-agent personas covering the full software engineering lifecycle, freelance client management, and content growth under the [Agent Skills Open Specification](https://agentskills.io).

## Engineering Standards & Skills
When responding to engineering prompts in this workspace, follow the standardized workflows located in `skills/`. Every skill folder contains a canonical `SKILL.md` and dual-agent personas (`agents/generator.md` and `agents/validator.md`):

- **Phase 1: Product & Architecture:** `prd-generator`, `trd-generator`, `app-flow`, `uiux-design-brief`, `backend-schema`, `system-architecture`, `implementation-plan`.
- **Phase 2: Execution & Quality:** `task-to-skill`, `playwright-e2e-testing`, `systematic-debugging`.
- **Phase 3: Auditing & Release:** `security-gap-audit`, `dead-code-cleanup`, `rigorous-code-review`, `clean-git-commits`.
- **Phase 4: Design Systems & Frontend:** `design-system-tokens`, `landing-page-converter`, `accessibility-wcag-audit`.
- **Phase 5: API, Database & Performance:** `api-contract-generator`, `db-migration-optimizer`, `performance-profiling`.
- **Phase 6: DevOps, CI/CD & FinOps:** `devops-docker-deploy`, `ci-cd-pipeline-builder`, `finops-token-optimizer`.
- **Phase 7: Freelance & Client Business Operations:** `freelance-client-onboarding`, `email-inbox-triage`, `invoice-billing-tracker`.
- **Phase 8: Social Growth, Content & Founder OS:** `insta-reel-creator`, `seo-content-strategist`, `social-copy-repurposer`, `executive-time-ledger`.

## Key Architectural Principles
- **Dual-Agent Peer Review:** Execute skills autonomously with peer-review using `python scripts/run.py --skill <name> --input "<prompt>" --mode dual`.
- **Two-Phase Enforcement:** High-risk tasks (security fixes, dead code pruning, refactors) enforce an **Audit / Verify First** stop before modifying code.
- **Atomic Commits:** Format all commits using Conventional Commits (`type(scope): summary`).
