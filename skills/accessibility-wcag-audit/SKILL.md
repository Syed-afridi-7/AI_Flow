---
name: accessibility-wcag-audit
description: Use when auditing web applications or component libraries for WCAG 2.1 AA/AAA accessibility compliance, identifying screen-reader, keyboard navigation, color contrast, and semantic ARIA flaws, and providing exact code remediation.
---

# Accessibility WCAG Audit

## Overview
Conducts rigorous accessibility evaluations against the Web Content Accessibility Guidelines (WCAG) 2.1 Level AA and AAA standards. Scans user interfaces, source code, and design tokens for perceivability, operability, understandability, and robustness barriers, delivering production-ready code remediations and manual testing verification scripts.

## When to Use
- **Trigger symptoms:** When preparing for pre-launch compliance certification, conducting accessibility health checks, remediating screen reader or keyboard traps, fixing low contrast or missing ARIA labels, or fulfilling legal accessibility mandates (ADA Title III, Section 508, European Accessibility Act).
- **When NOT to use:** Pure backend batch data processing pipelines, command-line utilities with no terminal UI, or headless daemon services.

## Instructions

Execute the accessibility audit and remediation through four standardized phases:

### Phase 1: Automated & Static Code Surface Analysis
1. **Semantic HTML Structure:** Audit DOM nodes for appropriate semantic elements (`<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, `<section>`, `<article>`). Enforce heading hierarchy (`<h1>` through `<h6>`) with zero skipped levels.
2. **First Rule of ARIA:** Flag any non-standard elements mimicking native controls (e.g., `<div onClick>` instead of `<button>`) and replace with native elements.
3. **Form Associations & Input Assistance:** Validate every form field has an explicitly linked `<label for="id">`, proper `aria-describedby` error bindings, and autocomplete attributes.
4. **Non-Text Content:** Check every `<img>` and `<svg>`: descriptive `alt` for informative graphics; `alt=""` or `aria-hidden="true"` for decorative icons.

### Phase 2: Contrast & Visual Perception Verification
1. **Mathematical Contrast Verification:**
   - Normal text (< 18pt / 24px, or < 14pt bold): minimum 4.5:1 contrast against surface background (WCAG 1.4.3).
   - Large text (&ge; 18pt / 24px, or &ge; 14pt bold): minimum 3.0:1 contrast.
   - Non-text UI controls and states (borders, checkboxes, focus rings): minimum 3.0:1 contrast against adjacent background (WCAG 1.4.11).
2. **Information Encoding:** Ensure color is never the sole vehicle for communicating status, errors, or required fields (WCAG 1.4.1).

### Phase 3: Keyboard Operability & Focus Management
1. **Keyboard Walkthrough:** Verify that every interactive control is reachable via `Tab` / `Shift+Tab` and activatable via `Enter` or `Space`.
2. **Zero Keyboard Traps:** Confirm focus can freely enter and exit all composite components (modals, dropdowns, tooltips) using standard keystrokes (WCAG 2.1.2).
3. **Focus Visibility & Order:** Enforce dedicated, high-contrast focus rings (`:focus-visible`). Prohibit `outline: none` without replacement.
4. **Modal & Dialog Trapping:** Verify modal dialogs contain focus while open (`aria-modal="true"`), auto-focus the first element, close on `Escape`, and return focus to the trigger on dismissal.

### Phase 4: Screen Reader & Dynamic State Auditing
1. **Live Regions:** Ensure dynamic alerts, asynchronous toast messages, and cart updates use appropriate `aria-live="polite"` or `role="alert"`.
2. **State Announcements:** Check dynamic disclosure widgets for explicit `aria-expanded="true|false"` and `aria-controls`.

## Rules & Constraints
- **Zero Critical Violations:** A passing audit requires zero Level A and AA blockers (no keyboard traps, unlabelled buttons, or invisible focus states).
- **Prefer Native HTML over ARIA:** Always replace ARIA workarounds with semantic HTML elements where available.
- **Provide Actionable Code Diffs:** Every finding must provide an exact `Before` vs. `After` code remediation block.
- **Never Suppress Focus Outlines:** Never deploy CSS that disables focus rings globally (`*:focus { outline: none }`).

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Correction |
| :--- | :--- |
| `<div onClick={...}>` as button | Use native `<button type="button">` with native keyboard & screen reader support. |
| Removing focus outlines for aesthetics | Implement custom `:focus-visible` styling with 3:1+ contrast rings. |
| Placeholder text as form label | Use persistent `<label>` tags; placeholders disappear and fail contrast. |
| Generic icon buttons without accessible names | Add `aria-label="Close dialog"` or visually hidden `<span class="sr-only">`. |
