# AGENTS.md - Agent Instructions & Skills Registry

This repository contains **AI_Flow**, a standardized framework of Agentic Skills for software development. Any AI agent operating within this workspace should refer to the skills catalog below to guide its behavior across the software lifecycle.

---

## 🧭 Multi-Agent Skills Registry

The skills below are defined in [`skills/`](./skills) and follow the [Agent Skills Specification](https://agentskills.io). Whenever a user request matches a skill's triggering conditions, load and execute the corresponding [`SKILL.md`](./skills):

| Skill Name | Location | Triggering Conditions |
| :--- | :--- | :--- |
| **`prd-generator`** | [`skills/prd-generator/SKILL.md`](./skills/prd-generator/SKILL.md) | Use when initiating a new product, defining scope for a major feature, or translating an unformed idea into a structured engineering specification before writing code. |
| **`trd-generator`** | [`skills/trd-generator/SKILL.md`](./skills/trd-generator/SKILL.md) | Use when translating product requirements into technical requirements, defining non-functional requirements, setting service SLAs, or establishing architectural constraints before implementation. |
| **`app-flow`** | [`skills/app-flow/SKILL.md`](./skills/app-flow/SKILL.md) | Use when mapping user navigation journeys, defining screen-to-screen transitions, designing state machines, or documenting edge-case flows and permission gates before frontend development. |
| **`uiux-design-brief`** | [`skills/uiux-design-brief/SKILL.md`](./skills/uiux-design-brief/SKILL.md) | Use when translating product requirements into UI/UX architecture, establishing visual design tokens, planning screen flows, or creating component contracts before frontend development. |
| **`backend-schema`** | [`skills/backend-schema/SKILL.md`](./skills/backend-schema/SKILL.md) | Use when designing database schemas, modeling relational or document entities, writing DDL table migrations, establishing foreign keys, or creating indexing strategies for query performance. |
| **`system-architecture`** | [`skills/system-architecture/SKILL.md`](./skills/system-architecture/SKILL.md) | Use when architecting a software system, selecting technology stacks, designing database schemas, defining API contracts, or evaluating scalability and resilience trade-offs before implementation. |
| **`implementation-plan`** | [`skills/implementation-plan/SKILL.md`](./skills/implementation-plan/SKILL.md) | Use when breaking down feature specifications into phased engineering implementation plans, ordering task dependencies, establishing test checkpoints, or defining rollout stages. |
| **`task-to-skill`** | [`skills/task-to-skill/SKILL.md`](./skills/task-to-skill/SKILL.md) | Use when turning a completed engineering workflow, recurring process, or established problem-solving pattern into a permanent, reusable Agent Skill. |
| **`playwright-e2e-testing`** | [`skills/playwright-e2e-testing/SKILL.md`](./skills/playwright-e2e-testing/SKILL.md) | Use when setting up end-to-end testing, configuring Playwright for a web application, identifying critical user journeys, or writing resilient automated browser tests. |
| **`systematic-debugging`** | [`skills/systematic-debugging/SKILL.md`](./skills/systematic-debugging/SKILL.md) | Use when investigating bugs, runtime exceptions, failing automated tests, or unexpected system behavior to isolate root causes before writing code fixes. |
| **`security-gap-audit`** | [`skills/security-gap-audit/SKILL.md`](./skills/security-gap-audit/SKILL.md) | Use when conducting a pre-launch security review, vulnerability assessment, threat model audit, or scanning a codebase for authentication, authorization, injection, and secrets risks. |
| **`dead-code-cleanup`** | [`skills/dead-code-cleanup/SKILL.md`](./skills/dead-code-cleanup/SKILL.md) | Use when identifying and safely removing unused files, obsolete dependencies, dead imports, orphaned functions, commented-out blocks, or duplicated code across a codebase. |
| **`rigorous-code-review`** | [`skills/rigorous-code-review/SKILL.md`](./skills/rigorous-code-review/SKILL.md) | Use when conducting a code review on pull requests, git diffs, or staged changes to verify correctness, detect regressions, evaluate performance, and catch security flaws before merging. |
| **`clean-git-commits`** | [`skills/clean-git-commits/SKILL.md`](./skills/clean-git-commits/SKILL.md) | Use when staging changes, splitting work into atomic commits, writing Conventional Commits messages, or preparing clean git pull request histories. |

---

## 🛡️ Global Agent Rules

1. **Verify Before Action:** For high-impact actions (audits, dead code deletion, security fixes, large refactors), always perform an audit / verification step and obtain user confirmation before altering production code.
2. **Never Shotgun Debug:** Adhere strictly to the 5-step hypothesis and proof protocol in [`skills/systematic-debugging/SKILL.md`](./skills/systematic-debugging/SKILL.md).
3. **Keep Commits Clean & Atomic:** Every commit must follow Conventional Commits and pass builds independently per [`skills/clean-git-commits/SKILL.md`](./skills/clean-git-commits/SKILL.md).
