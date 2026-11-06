---
name: prd-generator
description: Use when initiating a new product, defining scope for a major feature, or translating an unformed idea into a structured engineering specification before writing code.
---

# PRD Generator

## Overview
A Product Requirements Document (PRD) establishes the problem space, target personas, MVP boundaries, data models, and measurable success criteria. This skill forces a mandatory discovery phase before generating the specification to eliminate ambiguous assumptions.

## When to Use
- **Trigger symptoms:** Starting a greenfield project, introducing a major feature, evaluating feature scope, or user says "create a PRD for [idea]" or "write requirements for [idea]".
- **When NOT to use:** Routine bug fixes, minor UI tweaks, or when detailed specifications and acceptance criteria already exist.

## Instructions

### Phase 1: Clarifying Discovery (Mandatory Stop)
Before generating any part of the PRD:
1. Ask the user up to **5 targeted clarifying questions** addressing:
   - The primary target user persona and their core pain point.
   - Must-have MVP scope vs. nice-to-have v2/v3 scope.
   - Technical, regulatory, or platform constraints (e.g., mobile-first, offline, self-hosted, cloud).
   - The explicit definition of "done" (acceptance criteria).
2. **STOP AND WAIT** for user responses. Do not draft requirements or make assumptions before receiving answers.

### Phase 2: Specification Generation
Once clarifying answers are received, output the PRD using the following structured sections:

1. **Problem Statement:** Who hurts, the exact friction, and why existing workarounds are inadequate.
2. **Target Personas:** 2 detailed personas with roles, primary workflows, and pain points.
3. **Goals & Non-Goals:** Explicit list of what this release WILL and WILL NOT accomplish.
4. **User Stories:** Formatted as `"As a [persona], I want [action] so that [benefit]"`, each with testable acceptance criteria.
5. **Feature Scope Matrix:** Strict breakdown into **MVP**, **v2**, and **Later (Icebox)**.
6. **Detailed Functional Requirements:** Numbered, unambiguous requirements for each MVP feature.
7. **Data Model Sketch:** Entities, key attributes, relationships, and constraint definitions.
8. **Edge Cases & Failure States:** Network outages, invalid inputs, unauthorized access, concurrency issues.
9. **Success Metrics (KPIs):** Measurable targets (e.g., onboarding completion > 85%, p95 latency < 200ms).
10. **Open Questions & Risks:** Unresolved technical, legal, or UX unknowns flagged explicitly.

## Rules & Constraints
- Be opinionated and specific. Avoid generic filler like "fast and user-friendly".
- Never invent ambiguous business logic. If a requirement is unclear, flag it under Open Questions.
- Strictly separate MVP from subsequent versions. Resist scope creep.

## Rationalization Table
| Temptation / Excuse | Reality |
| :--- | :--- |
| "The idea seems simple enough to skip questions." | Simple ideas carry the most implicit assumptions. Ask first. |
| "I'll answer the clarifying questions myself." | Assumptions guarantee rework. The user must define their vision. |
| "I'll include nice-to-haves in the MVP section." | Scope bloat delays delivery. Push secondary features to v2/Later. |
