---
name: playwright-e2e-testing
description: Use when setting up end-to-end testing, configuring Playwright for a web application, identifying critical user journeys, or writing resilient automated browser tests.
---

# Playwright E2E Testing

## Overview
Establishes a production-grade End-to-End (E2E) testing suite using Playwright. Enforces resilient locator strategies, shared authentication fixtures, test data seeding/cleanup, and CI workflow integration.

## When to Use
- **Trigger symptoms:** When setting up browser automation, testing frontend web applications, preventing regression bugs across user flows, or when user requests "setup Playwright" or "write E2E tests".
- **When NOT to use:** Pure unit testing of utility functions, backend database unit tests, or headless API contract tests without browser interaction.

## Instructions

Execute the testing setup through these sequential steps:

1. **Stack Detection & Configuration:**
   - Detect web server port, build commands, and frontend framework.
   - Generate `playwright.config.ts` supporting local dev + headless CI runs.
   - Configure retries (`retries: process.env.CI ? 2 : 0`), screenshots on failure, and trace capture (`trace: 'on-first-retry'`).
2. **User Journey Inventory & Approval Gate (MANDATORY STOP):**
   - Inspect routing and components to list critical user journeys (e.g., Auth &rarr; Onboarding &rarr; Core Action &rarr; Checkout).
   - **Stop and present journeys to the user.** Do not author test files until journeys are approved.
3. **Resilient Selectors & DOM Attributes:**
   - Prefer user-facing role selectors (`getByRole`, `getByLabel`, `getByText`).
   - If dynamic elements require dedicated test hooks, add `data-testid` attributes directly to components.
   - Never rely on fragile XPath or deeply nested CSS class chains.
4. **Authentication Fixtures:**
   - Implement storage-state reuse (`playwright/.auth/user.json`) to bypass redundant UI login sequences across authenticated test specs.
5. **Data Seeding & Isolation:**
   - Implement database seeding and teardown helpers so tests run in isolation with idempotent state.
6. **NPM Scripts & CI Integration:**
   - Add scripts to `package.json`:
     - `test:e2e`: standard headless execution
     - `test:e2e:ui`: interactive Playwright UI mode
     - `test:e2e:ci`: CI execution with JUnit/HTML reporting
   - Provide a GitHub Actions workflow (`.github/workflows/e2e.yml`) that runs tests on Pull Requests and uploads trace artifacts on failure.

## Rules & Constraints
- Never use arbitrary `page.waitForTimeout(5000)`. Always await observable web-first assertions (`toBeVisible()`, `toHaveText()`).
- Always verify all tests pass locally before declaring completion.
