# GitHub Copilot Instructions

## Repository Overview
This repository provides **AI_Flow**, a standardized set of Agentic Skills covering the end-to-end software development lifecycle.

## Engineering Standards & Skills
When responding to engineering prompts in this workspace, follow the standardized workflows located in `skills/`:
- **Product Definition (`skills/prd-generator/SKILL.md`)**: Clarify scope, personas, and acceptance criteria before writing specifications.
- **Technical Requirements (`skills/trd-generator/SKILL.md`)**: Define throughput, latency budgets, availability SLAs, and compliance boundaries.
- **App Flow (`skills/app-flow/SKILL.md`)**: Map screen-to-screen transitions, state machines, and edge-case error flows.
- **UI/UX Design (`skills/uiux-design-brief/SKILL.md`)**: Define tokens, responsive layout rules, component states, and accessibility standards.
- **Backend Schema (`skills/backend-schema/SKILL.md`)**: Design ERDs, DDL tables, foreign key cascades, and high-performance composite indexes.
- **Architecture (`skills/system-architecture/SKILL.md`)**: Specify high-level topology, DB schemas, API contracts, and resilience policies.
- **Implementation Plan (`skills/implementation-plan/SKILL.md`)**: Break down work into atomic, dependency-ordered engineering tasks.
- **Testing (`skills/playwright-e2e-testing/SKILL.md`)**: Setup resilient E2E Playwright tests with user-facing locators and auth fixtures.
- **Debugging (`skills/systematic-debugging/SKILL.md`)**: Restate problem, hypothesize causes, verify with probes, and apply minimal fixes.
- **Security (`skills/security-gap-audit/SKILL.md`)**: Audit for auth, IDOR, injection, and secrets vulnerabilities without modifying code until confirmed.
- **Dead Code (`skills/dead-code-cleanup/SKILL.md`)**: Audit unused files and dependencies first; execute only with explicit consent.
- **Git Commits (`skills/clean-git-commits/SKILL.md`)**: Format all commits using Conventional Commits (`type(scope): summary`).
