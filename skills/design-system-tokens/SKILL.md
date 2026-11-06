---
name: design-system-tokens
description: Use when establishing, extracting, structuring, or maintaining multi-tier design tokens (global primitives, semantic aliases, and component-level tokens) across CSS custom properties, Tailwind configuration, Style Dictionary, or Figma design-to-code pipelines.
---

# Design System Tokens

## Overview
Establishes a scalable, multi-tier design token architecture following the Design Tokens Community Group (DTCG) W3C specification. Bridges the gap between UI/UX design decisions and production frontend code by formalizing colors, typography, spacing, elevations, motion, and border radii into deterministic, platform-agnostic token dictionaries.

## When to Use
- **Trigger symptoms:** When starting a new design system, migrating from hardcoded CSS/Tailwind values, establishing dark mode / multi-theme support, syncing Figma design tokens with codebases, or creating cross-platform design constants (Web, React Native, iOS, Android).
- **When NOT to use:** Ad-hoc single-page prototypes with no reusable component needs, backend API microservices, or trivial one-off bugfixes that do not introduce new design variables.

## Instructions

Execute the design token architecture across four standardized phases:

### Phase 1: Primitive Token Definition (Global Tier)
1. **Raw Color Palette:** Define raw hue scales from 50 to 950 using consistent perceptual spaces (e.g., OKLCH or HSL) for neutrals, brand primaries, accents, and status hues (success, warning, error, info).
2. **Typography Scales:** Define font families (sans, serif, mono), modular scale steps (xs through 5xl), font weights (400, 500, 600, 700), and proportional line heights.
3. **Spatial & Layout Units:** Establish a consistent base grid (4px or 8px), spacing steps (0 through 96), and border-radius presets (none, sm, md, lg, xl, full).
4. **Elevation & Shadows:** Define multi-layered shadow tokens representing ambient and direct light elevations (0 through 5).
5. **Motion Tokens:** Define standard duration curves (100ms to 500ms) and easing functions (standard, enter, exit).

### Phase 2: Semantic Token Mapping (System Tier)
1. Map raw primitives to contextual intent tokens:
   - Surface & Backgrounds: `--color-surface-base`, `--color-surface-raised`, `--color-surface-overlay`.
   - Text & Content: `--color-text-primary`, `--color-text-secondary`, `--color-text-muted`, `--color-text-inverse`.
   - Actions & Accents: `--color-action-primary-default`, `--color-action-primary-hover`, `--color-action-primary-active`.
   - Feedback & Borders: `--color-border-subtle`, `--color-border-strong`, `--color-feedback-error-bg`, `--color-feedback-error-text`.
2. Construct **Light and Dark theme parity** where semantic tokens remap seamlessly to appropriate primitives without altering component code.

### Phase 3: Component-Scoped Token Layer (Component Tier)
1. Provide component override tokens where isolation is critical (e.g., `--btn-primary-bg: var(--color-action-primary-default)`).
2. Ensure strict encapsulation: components never reference Tier 1 primitives directly.

### Phase 4: Platform Transformation & Export
1. **DTCG JSON Specification:** Generate valid `$value`, `$type`, and `$description` properties.
2. **CSS Custom Properties:** Produce `:root` and `[data-theme="dark"]` stylesheet blocks.
3. **Tailwind CSS Extension:** Generate a `theme.extend` configuration block consuming semantic CSS variables.
4. **TypeScript Definitions:** Export typed token interfaces with full auto-completion and documentation comments.

## Rules & Constraints
- **Strict Tier Separation:** Components must NEVER consume Tier 1 raw primitives directly; all consumption must flow through Tier 2 semantic aliases.
- **Dark Mode Parity:** Every semantic color token defined in the light theme must have an intentional, contrast-verified counterpart in the dark theme.
- **Contrast Guarantee:** Normal body text against its paired surface must maintain a minimum contrast ratio of 4.5:1 (WCAG AA). Large text must maintain at least 3.0:1.
- **Single Source of Truth:** All platform code (CSS, Tailwind, TypeScript) must be generated or mapped deterministically from the central token schema.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Correction |
| :--- | :--- |
| Hardcoding hex values in component styling | Map all hex values to Tier 1 primitives, then Tier 2 semantic variables. |
| Inverting black/white crudely for dark mode | Design dark surfaces with elevation lightness layering and desaturated accent colors. |
| Missing `$type` annotations in token JSON | Adhere to DTCG standard by including explicit `$type` (`color`, `dimension`, etc.). |
| Over-fragmenting tokens with 10+ tiers | Limit hierarchy to exactly 3 tiers: Global Primitives &rarr; Semantic Aliases &rarr; Component Tokens. |
