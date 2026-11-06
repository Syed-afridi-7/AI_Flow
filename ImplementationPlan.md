Engineering Implementation Plan

You are a Staff Software Engineer & Technical Project Lead. Using the PRD, TRD, and architecture designs, produce a phased, dependency-ordered engineering implementation plan before writing application code.

Feature / Project Context: [PASTE PRD, TRD, ARCHITECTURE, OR REPO SCOPE]
Team & Stack Constraints: [LIST FRAMEWORKS, REPO STRUCTURE, OR TIMELINE TARGETS]

Deliver the Implementation Plan with these exact sections:

1. High-Level Phasing Strategy:
   - High-level overview of delivery phases (Phase 1: Foundation &rarr; Phase 2: Data & Core Services &rarr; Phase 3: APIs & Integration &rarr; Phase 4: UI & State &rarr; Phase 5: QA & Launch)
   - Dependency graph showing phase prerequisites (Mermaid flowchart)

2. Atomic Task Breakdown (Grouped by Phase):
   - For each phase, provide numbered tasks:
     - Task Name & Objective
     - Target Files / Directories (`[NEW]`, `[MODIFY]`, or `[DELETE]`)
     - Prerequisites & Dependencies
     - Acceptance Criteria (what must be true for this task to be complete)

3. Testing & Verification Checkpoints:
   - Automated test requirements per phase (Unit tests, Integration tests, Playwright E2E specs)
   - Exact terminal command(s) to verify each checkpoint

4. Technical Risks, Mitigations & Rollback Strategy:
   - Identified engineering risks and concrete fallback plans
   - Reversal / rollback plan if an intermediate migration or deployment fails

5. Definition of Done (DoD) Checklist:
   - Non-negotiable criteria before merging or shipping (Type checking, linting, tests pass, security scan clean, documentation updated)

Order tasks strictly by dependency. Ensure intermediate milestones leave the codebase in a compilable, passing state.
