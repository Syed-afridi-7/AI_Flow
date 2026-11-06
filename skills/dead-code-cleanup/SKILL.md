---
name: dead-code-cleanup
description: Use when identifying and safely removing unused files, obsolete dependencies, dead imports, orphaned functions, commented-out blocks, or duplicated code across a codebase.
---

# Dead Code Cleanup & Refactoring

## Overview
A two-phase protocol for safely pruning dead code, obsolete files, and duplicate logic without causing breaking runtime regressions. Enforces a strict read-only audit phase before performing any deletions.

## When to Use
- **Trigger symptoms:** Codebase bloat, stale components after feature deprecations, high technical debt, or when the user says "clean up dead code", "remove unused imports", or "refactor duplicate logic".
- **When NOT to use:** While actively writing a feature or debugging an active bug.

## The Two-Phase Contract

### Phase 1: Audit & Discovery (Make ZERO Code Changes)
Perform a comprehensive audit and produce an evidence table:
1. **Unused Files & Modules:** Components, utilities, types, or routes with zero incoming references.
2. **Unused Exports & Variables:** Functions, constants, or types exported but never imported.
3. **Obsolete Dependencies:** Packages listed in `package.json`, `pyproject.toml`, or `Cargo.toml` with zero imports.
4. **Orphaned Environment Variables & Endpoints:** Declared env keys or routes no longer called.
5. **Commented-Out Code:** Legacy blocks left behind without clear explanatory intent.
6. **Duplicated Logic:** Identical or near-identical algorithms implemented in 2+ locations.
7. **Oversized Files:** Files that have grown beyond single-responsibility boundaries.

#### Audit Output Table
For every identified candidate, provide:
| Item / Path | Type | Evidence of Inactivity | Confidence (%) | Risk Level (Low/Med/High) | Proposed Action |
| :--- | :--- | :--- | :--- | :--- | :--- |

> [!WARNING]
> Flag anything with less than **90% confidence** (e.g., dynamically imported modules, reflection, public library exports). Do **NOT** propose deletion for items below 90% confidence.

**STOP AND WAIT:** Halt execution immediately after outputting the audit table. Wait for explicit user confirmation.

---

### Phase 2: Execution (ONLY After User Approval)
Upon receiving approval:
1. Delete only the approved items.
2. Extract verified duplicate logic into shared utilities.
3. Split oversized files along distinct responsibility boundaries.
4. Run all existing tests and verify that the build succeeds without warnings.

## Rules & Constraints
- **Zero Behavioral Divergence:** Application behavior, API outputs, and UI interactions must remain 100% identical.
- **No New Dependencies:** Do not install third-party libraries to clean up dead code.
- **Preserve Public Contracts:** Never rename or remove public API signatures used by external consumers.

## Rationalization Table
| Temptation / Excuse | Reality |
| :--- | :--- |
| "It's obvious this file is unused, I'll delete it right away." | Dynamic imports or build plugins may load it. Audit and verify first. |
| "I can fix this small bug while cleaning up." | Mixing bug fixes with dead code removal creates confusing commit history. |
| "Tests passed, so deleting this exported helper is safe." | Unit tests may not cover external library consumers or sub-packages. |
