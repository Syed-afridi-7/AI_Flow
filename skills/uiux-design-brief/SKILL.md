---
name: uiux-design-brief
description: Use when translating product requirements into UI/UX architecture, establishing visual design tokens, planning screen flows, or creating component contracts before frontend development.
---

# UI/UX Design Brief

## Overview
Transforms functional specifications into a complete design architecture. Establishes intentional visual design tokens, screen inventories, user flows, component states, and accessibility standards prior to writing markup or styling.

## When to Use
- **Trigger symptoms:** When receiving a PRD, starting frontend development, designing new screen interfaces, standardizing design tokens, or establishing design systems.
- **When NOT to use:** Pure backend services, headless CLI utilities, or minor copy edits.

## Instructions

Produce the design brief adhering to these 10 deliverables:

1. **Design Principles:** 3 non-negotiable rules this product's interface must obey (e.g., "Speed over animation", "Dense data with high contrast").
2. **Visual Direction & Mood:** Typography and aesthetic tone, visual references, and explicitly what visual tropes to avoid.
3. **Design Tokens:**
   - **Color Palette:** Hex codes, semantic token names (`--bg-primary`, `--accent`, `--border`), and explicit usage rules.
   - **Typography Scale:** Font family, sizes, weights, and line-heights.
   - **Spacing & Elevation Scale:** Base unit (e.g., 4px/8px), margin/padding steps, border radius, box shadows.
4. **Screen Inventory:** Exhaustive table of every screen/modal with its URL route and core purpose.
5. **User Flows:** Step-by-step state transitions for every primary user journey.
6. **Per-Screen Layout Architecture:** Section breakdowns, visual hierarchy, primary/secondary action placements, and component groupings.
7. **Component Library Specification:** Reusable components, variants (e.g., primary, outline, ghost), and interactive states (default, hover, focus, active, disabled).
8. **Comprehensive Screen States:** Document layout and copy for **Empty**, **Loading (Skeleton)**, **Error**, **Success**, and **Offline** states.
9. **Responsive Behavior:** Breakpoint rules (mobile < 640px, tablet < 1024px, desktop >= 1024px) detailing stack vs. grid reflows.
10. **Accessibility & Usability:** WCAG 2.1 AA compliance targets, contrast ratios, keyboard navigation order, focus indicators, and ARIA landmarks.

## Rules & Constraints
- Justify every design choice: explain *why* a particular font, layout, or color palette serves this specific product.
- Avoid generic default templates and unstyled grey placeholders.
- Every interactive element must account for all 5 states (default, hover, focus, active, disabled).

## Common Mistakes
| Mistake | Correction |
| :--- | :--- |
| Omitting empty/error states | Every screen must have a designed empty slate and error recovery action. |
| Neglecting keyboard navigation | Specify focus rings and tab order alongside mouse clicks. |
| Arbitrary colors without semantic tokens | Map every color to a semantic variable token with defined contrast ratios. |
