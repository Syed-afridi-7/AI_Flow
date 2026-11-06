---
name: ai-flow
description: Use when building software end-to-end, executing autonomous dual-agent workflows, managing product specs, architecture, debugging, security audits, frontend design, DevOps, or freelance operations across the AI_Flow 8-phase lifecycle.
---

# AI_Flow: 8-Phase Autonomous Dual-Agent Lifecycle

## Overview
**AI_Flow** is a comprehensive, production-grade 30-skill, 60-agent autonomous software engineering and founder operating system. Compliant with the Agent Skills Open Specification (agentskills.io), it equips AI agents with 30 specialized skills structured across 8 lifecycle phases with Generator and Validator dual-agent review loops.

---

## When to Use
Use when executing any phase of the end-to-end software development lifecycle or founder operations:

| Phase | Core Skills Included | Trigger / User Intent |
| :--- | :--- | :--- |
| **Phase 1: Product & Architecture** | `prd-generator`, `trd-generator`, `app-flow`, `uiux-design-brief`, `backend-schema`, `system-architecture`, `implementation-plan` | PRDs, technical specs, screen navigation, ERDs, system topology, task plans |
| **Phase 2: Execution & Quality** | `task-to-skill`, `playwright-e2e-testing`, `systematic-debugging` | Converting workflows to skills, browser E2E tests, 5-step empirical debugging |
| **Phase 3: Auditing & Release** | `security-gap-audit`, `dead-code-cleanup`, `rigorous-code-review`, `clean-git-commits` | 10 threat vectors, dead code pruning, blocker/crash reviews, atomic git commits |
| **Phase 4: Design Systems & Frontend** | `design-system-tokens`, `landing-page-converter`, `accessibility-wcag-audit` | DTCG tokens, light/dark mode, SaaS landing pages, WCAG AA audits |
| **Phase 5: API, DB & Performance** | `api-contract-generator`, `db-migration-optimizer`, `performance-profiling` | REST contracts, zero-downtime DB migrations, Core Web Vitals, memory profiles |
| **Phase 6: DevOps, CI/CD & FinOps** | `devops-docker-deploy`, `ci-cd-pipeline-builder`, `finops-token-optimizer` | Multi-stage Docker, GitHub Actions CI/CD, prompt caching & token savings |
| **Phase 7: Freelance & Client Ops** | `freelance-client-onboarding`, `email-inbox-triage`, `invoice-billing-tracker` | SOW contracts, inbox P0-P5 triage, itemized invoices & dunning notices |
| **Phase 8: Social Growth & Founder OS** | `insta-reel-creator`, `seo-content-strategist`, `social-copy-repurposer`, `executive-time-ledger` | Spoken reel scripts, topic clusters, PR-to-social threads, founder calendar audits |

---

## Instructions

### 1. Identify Intent & Select Skill
Identify the specific lifecycle phase or skill requested by the user from the Routing Map above. Delegate execution directly to the designated skill specification in `skills/<skill-name>/SKILL.md` or invoke its dual-agent Generator/Validator pair.

### 2. Dual-Agent Generator-Validator Pattern
For each task:
1. **Generator (Persona A):** Produces the initial draft, code, plan, or specification.
2. **Validator (Persona B):** Adversarially evaluates the deliverable against the rubric (aiming for score >= 85/100).
3. **Self-Correction:** If blockers or failures are identified, self-correct before presenting to the user.

### 3. Core Operating Rules
- **Verify Before Action:** For security fixes, dead code removal, or schema migrations, produce an audit first and obtain user confirmation before making destructive edits.
- **Never Shotgun Debug:** Follow the 5-step protocol (restate, 3 hypotheses, probe, verify, minimal fix).
- **Never Hallucinate Requirements:** Ask up to 5 clarifying questions if constraints are ambiguous.
- **Dependency-First Execution:** Order work strictly by dependencies (PRD -> TRD -> App Flow -> Schema -> Plan -> Code & Tests).
- **Clean Atomic Commits:** Adhere to Conventional Commits format (`type(scope): summary`).
