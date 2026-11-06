---
name: systematic-debugging
description: Use when investigating bugs, runtime exceptions, failing automated tests, or unexpected system behavior to isolate root causes before writing code fixes.
---

# Systematic Debugging

## Overview
A strict, disciplined 5-step root-cause debugging protocol. Forbids "shotgun changes", premature fixes, and refactoring unrelated code before the exact root cause has been verified with evidence.

## When to Use
- **Trigger symptoms:** Application crashes, runtime stack traces, test suite failures, unexpected API responses, regression bugs, or when the user says "fix this error" or "why is this failing".
- **When NOT to use:** Routine feature development, greenfield implementation, or deliberate code refactoring when behavior is already correct.

## The Iron Law of Debugging
```
NEVER MODIFY PRODUCTION CODE BEFORE VERIFYING THE ROOT CAUSE WITH EVIDENCE.
```

## Instructions

Follow this exact 5-step sequence:

### Step 1: Restate & Align
Restate the problem clearly in your own words:
- **Observed Behavior:** What actually happens (including error codes and stack traces).
- **Expected Behavior:** What should happen under correct operation.
- Confirm alignment before investigating.

### Step 2: Formulate Ranked Hypotheses
List 3 to 5 distinct root causes ranked by probability. For each hypothesis, explain the concrete technical mechanism that could cause the observed symptoms.

### Step 3: Minimal Verification Probe
For each hypothesis, propose the single fastest, non-destructive check to confirm or eliminate it:
- A targeted log statement.
- A one-line assertion or REPL check.
- An inspection of environment variables, headers, or database rows.

### Step 4: STOP AND VERIFY (Mandatory Stop)
**Stop and wait.** Run the verification check or ask the user to provide the test output. Do not propose a code fix in this turn.

### Step 5: Implement the Minimal Fix
Only after the root cause is proven:
1. Make the smallest possible change that directly addresses the verified fault.
2. Explain specifically *why* this fix resolves the failure mechanism without side-effects.
3. Provide the exact steps or automated test command needed to verify the fix.

## Prohibitions & Red Flags
- ❌ **No Shotgun Fixes:** Never change multiple files simultaneously hoping one resolves the error.
- ❌ **No Unprompted Refactoring:** Never clean up, rename, or reformat surrounding code while debugging.
- ❌ **No "It Might Be...":** Never apply a code change based on pure guesswork without an empirical check.

## Rationalization Table
| Excuse / Shortcut | Reality |
| :--- | :--- |
| "I've seen this error before, I know the fix." | Similar errors often have completely different root causes. Verify first. |
| "A quick edit will test my theory faster." | Code changes introduce secondary variables and mask the real bug. |
| "While I'm here, I'll clean up this adjacent function." | Conflating fixes with refactors makes regressions impossible to isolate. |
