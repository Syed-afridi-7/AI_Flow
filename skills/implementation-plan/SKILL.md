---
name: implementation-plan
description: Use when breaking down feature specifications into phased engineering implementation plans, ordering task dependencies, establishing test checkpoints, or defining rollout stages.
---

# Engineering Implementation Plan

## Overview
Acts as a Staff Software Engineer and Technical Project Lead to transform specifications (PRD, TRD, Architecture, and Schema) into a phased, dependency-ordered implementation roadmap. Enforces atomic work units, explicit file paths, intermediate verification checkpoints, and clear Definition of Done standards.

## When to Use
- **Trigger symptoms:** Prior to writing application code for a feature, when organizing a large sprint, when breaking down complex architectures into incremental PRs, or when user asks "create an implementation plan", "break down these tasks", or "plan the engineering steps".
- **When NOT to use:** Writing code fixes for a single isolated bug, writing one-off documentation, or running manual tests.

## Instructions

Produce the Implementation Plan across these 5 structured sections:

### 1. Phasing Strategy & Dependency Graph
- Group development into logical, sequential phases:
  - **Phase 1: Foundation & Infrastructure** (scaffolding, dependencies, configs)
  - **Phase 2: Data Persistence & Models** (migrations, schemas, repositories)
  - **Phase 3: Core Business Logic & APIs** (services, endpoints, validations)
  - **Phase 4: Frontend UI & Client State** (components, routing, API hooks)
  - **Phase 5: Verification & Hardening** (E2E tests, security audits, load checks)
- Provide a Mermaid dependency flowchart (`flowchart LR`) showing phase blockers and parallel tracks.

### 2. Atomic Task Breakdown
For every task within each phase, document:
- **Task ID & Summary:** Concise, imperative action (e.g., `Task 2.1: Implement User Authentication Repository`).
- **Files Affected:** Explicit paths demarcated with `[NEW]`, `[MODIFY]`, or `[DELETE]`.
- **Dependencies:** Required preceding tasks.
- **Implementation Details:** Key functions, types, and logic to build.
- **Verification Criteria:** How to verify this specific task passes in isolation.

### 3. Verification Checkpoints
- Define exit criteria for each phase.
- Specify exact terminal commands to run (e.g., `npm run lint`, `npm test`, `npx prisma migrate dev`).
- Forbid advancing to subsequent phases if the current phase fails tests or introduces build breaks.

### 4. Technical Risks & Rollback Procedures
- Identify top 3 technical risks (e.g., third-party API rate limits, complex data migration locks).
- Concrete contingency and rollback strategies for each phase (e.g., backward-compatible database schema migrations).

### 5. Definition of Done (DoD)
A non-negotiable checklist that must be satisfied before closing the project/feature:
- [ ] All unit, integration, and E2E tests passing
- [ ] Zero TypeScript / linter compiler errors
- [ ] Pre-launch security scan clean
- [ ] No dead or commented-out code
- [ ] Atomic, conventional git commits

## Rules & Constraints
- Order tasks strictly by dependency: database schemas and types must precede API endpoints; API endpoints must precede UI client integration.
- Every task must leave the codebase in a compilable state.
- Keep tasks atomic: each task should be small enough to fit in a single, focused pull request.

## Rationalization Table
| Temptation / Shortcut | Reality |
| :--- | :--- |
| "We can jump straight to building UI screens." | UI built without backend contracts or data models requires heavy rewrites. |
| "Phase verification is too slow, we'll test at the end." | Finding foundational bugs in Phase 5 costs 10x more time than catching them in Phase 1. |
| "Task breakdown doesn't need file paths." | Omitting file paths leads to disorganized code placement and duplicate utilities. |
