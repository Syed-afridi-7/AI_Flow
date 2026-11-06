---
name: rigorous-code-review
description: Use when conducting a code review on pull requests, git diffs, or staged changes to verify correctness, detect regressions, evaluate performance, and catch security flaws before merging.
---

# Rigorous Code Review

## Overview
Acts as a Staff Software Engineer conducting an objective, non-performative code review on code diffs or pull requests. Focuses on functional correctness, regression hazards, performance bottlenecks, and security vulnerabilities over cosmetic nitpicks.

## When to Use
- **Trigger symptoms:** When a PR is opened, before merging a branch, reviewing staged git changes, or when the user says "review this PR", "check my code diff", or "give me feedback on these changes".
- **When NOT to use:** Brainstorming initial concepts or reviewing non-code plain text documentation.

## Instructions

Execute the review in two deliberate stages:

### Stage 1: Verification & Impact Analysis
Deeply inspect the diff against these 4 dimensions:
1. **Logic & Correctness:**
   - Does the implementation fulfill the stated intent without unintended side effects?
   - Are edge cases handled (empty collections, `null`/`undefined`, race conditions, unhandled rejections)?
   - Are there off-by-one errors or implicit type coercion bugs?
2. **Architecture & Contract Integrity:**
   - Does this adhere to existing project architectural patterns?
   - Does it break public interfaces, API contracts, or backward compatibility?
3. **Performance & Resource Safety:**
   - Unnecessary re-renders, N+1 database queries, memory leaks, or unclosed file/socket handles.
   - Algorithmic complexity hotspots (e.g., nested loops on unbounded data).
4. **Security & Resilience:**
   - Are inputs validated and sanitized at boundaries?
   - Are sensitive credentials or tokens exposed?
   - Are error states handled gracefully with user-facing recovery mechanisms?

### Stage 2: Structured Severity Categorization
Present all findings grouped strictly by severity:

- 🔴 **Blocker:** Must be resolved before merging. Bugs, data corruption risks, security vulnerabilities, or breaking contract changes.
- 🟡 **Warning:** Performance degradation, architectural drift, or maintainability concerns that should be addressed before release.
- 🟢 **Suggestion:** Non-blocking readability, typing improvements, or idiomatic enhancements.

#### Finding Format
For every **Blocker** and **Warning**, provide:
- **Location:** File path and line range (`[path/to/file#L45-L52]`).
- **Production Failure Scenario:** Exactly how this code fails in production (e.g., "If `items` is empty, `.reduce()` throws an unhandled TypeError, crashing the request worker.").
- **Remediation Diff:** The minimal, drop-in code fix.

## Rules & Constraints
- Provide actionable replacement code for every blocker.
- Never give performative rubber-stamp approvals ("Looks good to me!") when unhandled error conditions exist.
