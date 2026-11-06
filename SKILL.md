---
name: ai-flow
description: Use when building software end-to-end, writing PRDs or TRDs, designing app flows and UI/UX, modeling backend schemas, planning implementation roadmaps, debugging bugs, testing, auditing security, cleaning dead code, reviewing PRs, or formatting git commits.
---

# AI_Flow: Full-Lifecycle Software Engineering Skill

## Overview
**AI_Flow** is a comprehensive, production-grade software development lifecycle framework for AI coding assistants. It enforces structured rigor across every phase of development: requirements gathering (PRD), technical specifications (TRD), navigational flow mapping, visual tokens, backend schema modeling, implementation planning, automated testing, empirical debugging, security auditing, dead code pruning, code review, and version control.

---

## When to Use & Routing Map

Activate the corresponding module when the user prompt matches any of these triggers:

| User Intent / Trigger | Active Module | Core Deliverable |
| :--- | :--- | :--- |
| "Plan product", "write PRD", "feature spec" | **Module 1: PRD Generator** | 5-question discovery &rarr; PRD with user stories & MVP scope |
| "Technical requirements", "write TRD", "SLA", "latency budget" | **Module 2: TRD Generator** | Throughput, latency p95/p99, availability SLAs, compliance, DR |
| "App flow", "navigation map", "user transitions", "state machine" | **Module 3: App Flow Architecture** | Screen-to-screen transitions, permission gates, Mermaid state diagrams |
| "Design UI", "design tokens", "screen layout" | **Module 4: UI/UX Design Brief** | Tokens, screen inventory, states (empty/error), accessibility |
| "Database schema", "backend schema", "ERD", "table DDL", "indexes" | **Module 5: Backend Schema** | Mermaid ERD, exact SQL DDL, cascade rules, composite indexes |
| "Architecture", "tech stack", "API contracts", "system design" | **Module 6: System Architecture** | Mermaid topology, service boundaries, REST/gRPC endpoints |
| "Implementation plan", "task breakdown", "engineering roadmap" | **Module 7: Implementation Plan** | Phased dependency roadmap, atomic task files, test checkpoints |
| "Turn into skill", "remember this workflow" | **Module 8: Task to Skill** | Standalone Agent Skill specification with triggers and failure modes |
| "Setup E2E tests", "Playwright test", "browser test" | **Module 9: Playwright E2E Testing** | Resilient role locators, auth fixtures, data seeding, CI workflow |
| "Fix this error", "why is this failing", "debug this" | **Module 10: Systematic Debugging** | 5-step protocol: Restate &rarr; 3 hypotheses &rarr; probe &rarr; minimal fix |
| "Security audit", "find vulnerabilities", "check security" | **Module 11: Security Gap Audit** | Read-only scan of 10 threat vectors (Auth, IDOR, SQLi, Secrets, CORS) |
| "Clean dead code", "remove unused imports", "refactor" | **Module 12: Dead Code Cleanup** | Phase 1 confidence audit &rarr; Phase 2 execute only with user approval |
| "Review PR", "check diff", "code review" | **Module 13: Rigorous Code Review** | Stage 1 analysis &rarr; Stage 2 Blockers, Warnings, Suggestions |
| "Commit changes", "organize git", "write commit message" | **Module 14: Clean Git Commits** | Atomic commits adhering to Conventional Commits format |

---

## 🛡️ Core Operating Rules

1. **Verify Before Action:** For high-impact actions (security fixes, dead code deletion, large refactors), always perform an audit / verification step and obtain user confirmation before altering code.
2. **Never Shotgun Debug:** Forbid guessing or modifying multiple files at once. Verify the root cause with empirical evidence (log, assertion, query) before authoring fixes.
3. **Never Hallucinate Requirements:** If a business requirement or edge case is ambiguous, ask clarifying questions rather than inventing assumptions.
4. **Order by Dependency:** PRD &rarr; TRD &rarr; App Flow & UI/UX &rarr; Backend Schema & Architecture &rarr; Implementation Plan &rarr; Code & Tests.
5. **Keep Commits Clean & Atomic:** Every commit must represent exactly one logical change, pass builds and tests independently, and follow Conventional Commits.

---

## Detailed Skill Modules

### Module 1: PRD Generator
- **Phase 1 (Mandatory Discovery Stop):** Before drafting, ask up to 5 targeted questions regarding target persona, must-have MVP vs. v2 scope, technical constraints, and definition of done. **STOP AND WAIT** for user answers.
- **Phase 2 (Specification):** Output Problem Statement, 2 Target Personas, Goals & Non-Goals, User Stories, MVP Scope Matrix, Detailed Functional Requirements, Data Model Sketch, Edge Cases, Success Metrics (KPIs), and Open Questions.

---

### Module 2: Technical Requirement Document (TRD) Generator
- **Scope & Constraints:** Technical boundaries, supported platforms, explicit out-of-scope technical items.
- **Performance & Scalability:** Peak concurrency, read/write RPS, strict latency budgets (p50, p95, p99 < 150ms), horizontal/vertical scaling triggers.
- **Reliability & SLAs:** 99.9% uptime targets, circuit breakers, recovery metrics (RTO/RPO), automated backup cadences.
- **Security & Compliance:** Authentication lifecycles, RBAC matrices, encryption in transit (TLS 1.3) and at rest (AES-256), audit logging.
- **Integrations & Contracts:** Third-party timeouts, backoff with jitter, webhook idempotency keys.
- **Observability:** Structured JSON logs (`trace_id`, `span_id`), SLIs/SLOs, and APM error alerts.
- **Deployment Strategy:** Containerization, CI/CD quality gates, zero-downtime rolling/canary deployments.

---

### Module 3: App Flow & Navigation Architecture
- **Navigation Map:** Mermaid `flowchart TD` showing all routes, stacks, and modal hierarchies.
- **Screen Transitions Table:** Mapping each screen's route, entry points, user triggers, destination targets, and passed URL parameters.
- **Conditional Branching:** Auth guards, onboarding completion gates, role-based navigation.
- **State Machine Diagrams:** Mermaid `stateDiagram-v2` for complex multi-step workflows (Idle, Validating, Submitting, Success, Error).
- **Edge-Case & Interrupted Flows:** Network loss / offline banners, token expiration handling, unsaved changes confirmation dialogs, 404/500 recovery paths.
- **Deep Linking:** Canonical URL patterns and browser back/forward history behaviors.

---

### Module 4: UI/UX Design Brief
Deliver design principles (3 non-negotiable rules), visual mood and typography, complete design tokens (hex colors, 8px spacing, typography scale), screen inventory, user flows, per-screen layouts, component states (default, hover, focus, active, disabled), all 5 screen states (empty, loading skeleton, error, success, offline), responsive breakpoints, and WCAG AA accessibility standards.

---

### Module 5: Backend Schema & Data Architecture
- **ERD:** Visual entity relationships using Mermaid `erDiagram`.
- **SQL DDL Specifications:** Exact column types (`UUID`, `TIMESTAMPTZ`, `JSONB`, `NUMERIC`), primary keys, default values, check constraints, and foreign key cascades (`ON DELETE CASCADE / SET NULL / RESTRICT`).
- **Strategic Indexing:** Primary B-Tree indexes, composite indexes with column ordering (Filter &rarr; Sort), partial/filtered indexes (`WHERE deleted_at IS NULL`), and GIN indexes for JSON/search.
- **Normalization & Denormalization:** 3NF core with justified, synchronized denormalizations.
- **Audit Columns & Soft-Delete:** Standard `created_at`, `updated_at`, `deleted_at`, `created_by`.
- **Migration & Seed Plan:** Ordered migration files and deterministic development seed datasets.

---

### Module 6: System Architecture & Technical Specification
Mermaid system topology (`graph TD` or `sequenceDiagram`), tech stack trade-off justifications, API contracts (HTTP Method, Route, Payloads, Responses 200/400/401/404/500), caching layers, and resilience patterns.

---

### Module 7: Engineering Implementation Plan
- **Phasing Strategy:** Dependency-ordered phases (Foundation &rarr; Data &rarr; APIs &rarr; Frontend &rarr; QA &rarr; Deploy) with a Mermaid dependency graph (`flowchart LR`).
- **Atomic Task Breakdown:** Numbered tasks with affected files (`[NEW]`, `[MODIFY]`, `[DELETE]`), prerequisites, and acceptance criteria.
- **Verification Checkpoints:** Exact terminal commands to verify each phase before proceeding.
- **Technical Risks & Rollbacks:** Risk mitigation and concrete rollback procedures.
- **Definition of Done (DoD):** Non-negotiable checklist for merging to main.

---

### Module 8: Task to Skill Converter
Converts any completed task or repeating workflow into a permanent, reusable Agent Skill with frontmatter, triggers, instructions, constraints, output format, and failure modes.

---

### Module 9: Playwright E2E Testing
Stack detection, `playwright.config.ts`, user journey approval gate (STOP), resilient role-based selectors, auth fixtures (`storageState`), test data seeding/cleanup, and CI workflow.

---

### Module 10: Systematic Debugging (5-Step Protocol)
```
THE IRON LAW: NEVER MODIFY PRODUCTION CODE BEFORE VERIFYING THE ROOT CAUSE WITH EVIDENCE.
```
Restate &rarr; Formulate 3-5 ranked hypotheses &rarr; Minimal verification probe &rarr; STOP and verify &rarr; Minimal fix.

---

### Module 11: Security Gap Audit
Adversarial scan of 10 threat vectors (Auth, IDOR, Secrets, Injection, Route Protection, Validation, Rate Limiting, CORS/Headers, CVEs, Log Leaks). Ranked findings with exploit scenarios and code fixes. Zero code changes during audit.

---

### Module 12: Dead Code Cleanup & Refactoring
Two-phase contract: Phase 1 confidence-scored audit table with >90% confidence threshold &rarr; STOP and obtain approval &rarr; Phase 2 execute approved deletions without breaking contracts.

---

### Module 13: Rigorous Code Review
Two-stage review: Stage 1 verification (logic, performance, security, architecture) &rarr; Stage 2 structured findings (Blockers with production crash scenarios and drop-in fixes, Warnings, Suggestions).

---

### Module 14: Clean Conventional Git Commits
Summarize by intent, split into atomic commits (one logical change each), format with Conventional Commits (`type(scope): summary`), verify build at each step, and output exact git commands.
