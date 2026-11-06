---
name: ai-flow
description: Use when building software end-to-end, writing PRDs, designing UI/UX tokens, architecting systems, debugging bugs, generating Playwright E2E tests, conducting security audits, cleaning dead code, reviewing PRs, or formatting atomic git commits.
---

# AI_Flow: Full-Lifecycle Software Engineering Skill

## Overview
**AI_Flow** is a comprehensive, production-grade software development lifecycle framework for AI coding assistants. It enforces structured rigor across every phase of development: requirements gathering, visual architecture, system topology, automated testing, empirical debugging, security auditing, dead code pruning, code review, and version control.

---

## When to Use & Routing Map

Activate the corresponding module when the user prompt matches any of these triggers:

| User Intent / Trigger | Active Module | Core Deliverable |
| :--- | :--- | :--- |
| "Plan product", "write PRD", "feature spec" | **Module 1: PRD Generator** | 5-question discovery &rarr; PRD with user stories & MVP scope |
| "Design UI", "design tokens", "screen layout" | **Module 2: UI/UX Design Brief** | Tokens, screen inventory, states (empty/error), accessibility |
| "Architecture", "tech stack", "API contracts", "database schema" | **Module 3: System Architecture** | Mermaid topology, schema, indexing, REST/gRPC endpoints |
| "Turn into skill", "remember this workflow" | **Module 4: Task to Skill** | Standalone Agent Skill specification with triggers and failure modes |
| "Setup E2E tests", "Playwright test", "browser test" | **Module 5: Playwright E2E Testing** | Resilient role locators, auth fixtures, data seeding, CI workflow |
| "Fix this error", "why is this failing", "debug this" | **Module 6: Systematic Debugging** | 5-step protocol: Restate &rarr; 3 hypotheses &rarr; probe &rarr; minimal fix |
| "Security audit", "find vulnerabilities", "check security" | **Module 7: Security Gap Audit** | Read-only scan of 10 threat vectors (Auth, IDOR, SQLi, Secrets, CORS) |
| "Clean dead code", "remove unused imports", "refactor" | **Module 8: Dead Code Cleanup** | Phase 1 confidence audit &rarr; Phase 2 execute only with user approval |
| "Review PR", "check diff", "code review" | **Module 9: Rigorous Code Review** | Stage 1 analysis &rarr; Stage 2 Blockers, Warnings, Suggestions |
| "Commit changes", "organize git", "write commit message" | **Module 10: Clean Git Commits** | Atomic commits adhering to Conventional Commits format |

---

## 🛡️ Core Operating Rules

1. **Verify Before Action:** For high-impact actions (security fixes, dead code deletion, large refactors), always perform an audit / verification step and obtain user confirmation before altering code.
2. **Never Shotgun Debug:** Forbid guessing or modifying multiple files at once. Verify the root cause with empirical evidence (log, assertion, query) before authoring fixes.
3. **Never Hallucinate Requirements:** If a business requirement or edge case is ambiguous, ask clarifying questions rather than inventing assumptions.
4. **Keep Commits Clean & Atomic:** Every commit must represent exactly one logical change, pass builds and tests independently, and follow Conventional Commits.

---

## Detailed Skill Modules

### Module 1: PRD Generator
- **Phase 1 (Mandatory Discovery Stop):** Before drafting, ask up to 5 targeted questions regarding target persona, must-have MVP vs. v2 scope, technical constraints, and definition of done. **STOP AND WAIT** for user answers.
- **Phase 2 (Specification):** Output structured sections:
  1. Problem Statement (who hurts and why)
  2. Target Personas (2 realistic personas)
  3. Goals & Non-Goals
  4. User Stories (`"As a [role], I want [action] so that [benefit]"`)
  5. Feature Scope Matrix (MVP vs. v2 vs. Icebox)
  6. Detailed Functional Requirements per MVP feature
  7. Data Model Sketch (entities, relationships, constraints)
  8. Edge Cases & Failure States
  9. Success Metrics (KPIs)
  10. Open Questions & Risks

---

### Module 2: UI/UX Design Brief
Deliver a complete design brief before writing any frontend markup or styling:
1. **Design Principles:** 3 non-negotiable rules the UI must obey.
2. **Visual Direction:** Typography tone, visual mood, and what cliches to avoid.
3. **Design Tokens:** Semantic colors with hex values (`--bg-primary`, `--accent`), typography scale, 8px spacing scale, radius, elevation.
4. **Screen Inventory:** Table of all views with routes and primary objectives.
5. **User Flows:** Step-by-step state transitions for critical user journeys.
6. **Per-Screen Layout Architecture:** Visual hierarchy and component arrangement.
7. **Component Library Specification:** Reusable components, variants, and interactive states (default, hover, focus, active, disabled).
8. **Screen States:** Layouts for Empty, Loading (Skeleton), Error, Success, and Offline.
9. **Responsive Behavior:** Mobile (<640px), tablet (<1024px), desktop (>=1024px) reflow rules.
10. **Accessibility:** WCAG AA contrast ratios, keyboard navigation order, focus rings, and ARIA landmarks.

---

### Module 3: System Architecture & Technical Specification
Produce a production-ready architectural design:
1. **High-Level System Topology:** Mermaid diagram (`graph TD` or `sequenceDiagram`), service boundaries, communication protocols.
2. **Tech Stack Justification:** Languages, frameworks, persistence engines with explicit trade-off analysis (why chosen vs. rejected options).
3. **Data Architecture:** Schema design, data types, foreign keys, and indexing strategy for high-read/write paths.
4. **API Contracts:** Endpoints table (HTTP Method, Route, Auth, Request Payload, Responses 200/400/401/404/500), pagination, and caching headers.
5. **State Management & Data Flow:** Client cache (TanStack Query/SWR) vs. global state (Zustand/Redux), optimistic UI rollbacks.
6. **Non-Functional Requirements:** Latency budgets (p95 < 200ms), circuit breakers, exponential backoff retries, and structured logging.

---

### Module 4: Task to Skill Converter
Turn any completed task or repeating workflow into a reusable Agent Skill:
1. **Name:** Lowercase alphanumeric and hyphens only (`^[a-z0-9-]+$`).
2. **Description:** Frontmatter starting with `"Use when..."`, written in third person, describing symptoms and trigger situations without summarizing the workflow (<500 chars).
3. **Overview:** Core mental model in 1-2 sentences.
4. **Step-by-Step Instructions:** Sequential recipe written for an agent with zero prior context.
5. **Rules & Constraints:** Hard boundaries and rationalization counters.
6. **Output Format:** Exact template or code contract.
7. **Failure Modes:** Top 3-5 common mistakes and how to avoid them.

---

### Module 5: Playwright E2E Testing
1. **Configuration:** Setup `playwright.config.ts` with local web server detection, retries (`CI ? 2 : 0`), screenshots on failure, and trace capture.
2. **Journey Inventory & Approval Gate (STOP):** Inspect routes, list critical user journeys, and obtain user confirmation before writing specs.
3. **Resilient Selectors:** Prefer user-facing role locators (`getByRole`, `getByLabel`, `getByText`) or explicit `data-testid`. Never use fragile XPath or deep CSS class chains.
4. **Auth Fixtures:** Implement `storageState` caching to bypass repetitive UI login sequences.
5. **Data Isolation:** Implement seeding and cleanup hooks so tests run independently.
6. **CI Workflow:** Provide `.github/workflows/e2e.yml` running tests headless on Pull Requests.

---

### Module 6: Systematic Debugging (5-Step Protocol)
```
THE IRON LAW: NEVER MODIFY PRODUCTION CODE BEFORE VERIFYING THE ROOT CAUSE WITH EVIDENCE.
```
- **Step 1 (Restate):** Restate observed vs. expected behavior with exact error messages and stack traces.
- **Step 2 (Hypothesize):** List 3-5 ranked root causes with explicit failure mechanisms.
- **Step 3 (Probe):** Define the fastest non-destructive check for each hypothesis (a log line, one-line assertion, or environment check).
- **Step 4 (STOP & VERIFY):** **Stop and wait.** Execute or request verification results. Do not write fix code yet.
- **Step 5 (Minimal Fix):** Apply the smallest possible code change that eliminates the proven failure mechanism, and provide verification steps.

---

### Module 7: Security Gap Audit
Conduct an adversarial audit without modifying code:
1. **Systematic Scan Across 10 Vectors:**
   - Authentication & session flaws (weak hashing, token validation)
   - Authorization & IDOR (tenant isolation, role checks)
   - Hardcoded secrets and leaked credentials
   - Injection vulnerabilities (SQL, NoSQL, OS command, XSS)
   - Unprotected or unvalidated API endpoints
   - Missing input schema validation & sanitization
   - Missing rate limiting & brute-force protection
   - Permissive CORS, missing security headers, insecure cookie flags
   - Outdated dependencies with known CVEs
   - Telemetry/logging leaks of PII or sensitive tokens
2. **Findings Report:** Ranked Critical &rarr; High &rarr; Medium &rarr; Low. Include Location (`file#L10-L20`), Production Exploit Scenario, and Exact Remediation Diff.
3. **Explicit Clean Statement:** Report clean vectors explicitly rather than staying silent.
4. **SAFEGUARD:** Do NOT alter production code until findings are approved.

---

### Module 8: Dead Code Cleanup & Refactoring
- **Phase 1: Audit (Make ZERO Changes):** Search for unused files, unreferenced exports, obsolete dependencies, orphaned env vars, commented-out blocks, and duplicated logic.
  - Present an **Audit Output Table** with Path, Type, Evidence, Confidence (%), Risk Level, and Proposed Action.
  - Flag any candidate under **90% confidence** &mdash; do NOT delete low-confidence items.
  - **STOP AND WAIT:** Request explicit user approval.
- **Phase 2: Execution (Post-Approval Only):** Delete approved items, extract verified duplicate logic into shared utilities, split oversized files, and verify builds and tests pass cleanly.

---

### Module 9: Rigorous Code Review
- **Stage 1 (Verification):** Analyze logic correctness, edge cases (null/undefined, concurrency), architectural alignment, performance bottlenecks (N+1 queries, memory leaks), and security boundaries.
- **Stage 2 (Structured Findings):** Group findings strictly by severity:
  - 🔴 **Blocker:** Must be resolved before merge (bugs, security risks, breaking contract regressions). Include file/line, production crash scenario, and drop-in code fix.
  - 🟡 **Warning:** Architectural drift or performance degradation requiring remediation.
  - 🟢 **Suggestion:** Optional readability, typing, or doc polish.
- Never issue rubber-stamp approvals when unhandled exceptions or security flaws exist.

---

### Module 10: Clean Conventional Git Commits
1. **Summarize Intent:** Group staged and unstaged diffs by underlying engineering goal.
2. **Atomic Separation:** One logical change per commit. Separate bug fixes from refactorings.
3. **Conventional Commits Structure:**
   ```
   <type>(<optional scope>): <imperative summary under 60 chars>

   <Detailed body explaining WHY the change was made and any tradeoffs.>

   [BREAKING CHANGE: <description if applicable>]
   ```
   Allowed types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`.
4. **Build Safety:** Order commits so tests and builds succeed at every single commit in the chain.
5. **Exact Commands:** Output the exact `git add` and `git commit` commands to run.

---

## 🛑 Rationalization Table (Self-Check for Agents)

| Temptation / Shortcut | Reality & Mandatory Behavior |
| :--- | :--- |
| "This bug is simple, I'll jump straight to fixing it." | Similar errors often have subtle, different root causes. Always probe first. |
| "I'll delete this dead file right now without asking." | Build plugins or reflection may reference it. Audit and wait for approval. |
| "I'll answer the PRD questions myself to save time." | Assumptions guarantee rework. The human stakeholder must define their vision. |
| "I'll bundle all these changes into one commit." | Mega-commits ruin bisectability and code reviews. Split into atomic units. |
| "Everything looks good, I'll approve without deep checks." | Superficial reviews allow production crashes and security leaks. Audit thoroughly. |
