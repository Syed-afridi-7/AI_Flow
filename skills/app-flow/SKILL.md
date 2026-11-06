---
name: app-flow
description: Use when mapping user navigation journeys, defining screen-to-screen transitions, designing state machines, or documenting edge-case flows and permission gates before frontend development.
---

# App Flow & Navigation Architecture

## Overview
Acts as a Frontend Architect and Principal Product Designer to map end-to-end navigational flows, state transitions, conditional permission gates, and edge-case recoveries before frontend code is authored. Eliminates navigation dead ends and unhandled interaction states.

## When to Use
- **Trigger symptoms:** After UI/UX design brief completion, before building frontend routing/pages, when designing multi-step wizards or checkout flows, or when the user says "map the app flow", "design navigation paths", or "create state transition diagrams".
- **When NOT to use:** Pure backend batch scripts, API-only microservices without UI, or minor single-button style updates.

## Instructions

Produce the App Flow document across these 6 structured sections:

### 1. High-Level Navigation Map
- Visual architecture diagram using Mermaid (`flowchart TD`).
- Illustrate the entire routing hierarchy: Public landing pages, Authentication modals, Protected dashboard stacks, and Settings sub-routes.

### 2. Screen-to-Screen State Transitions Table
Exhaustively map each view:
| Screen Name | Route Path | Entry Point(s) | Primary User Action | Transition Target | Context / Query Params |
| :--- | :--- | :--- | :--- | :--- | :--- |

### 3. Conditional Branching & Access Gates
- **Auth Guard:** Strict logic directing unauthenticated visitors to `/login` with a `?redirect=` return parameter.
- **Onboarding Gate:** Redirection to onboarding wizards if mandatory user setup steps remain incomplete.
- **Role Guard:** Branching logic separating Admin, Member, and Viewer permissions.

### 4. Workflow State Machines
For all multi-step processes (e.g., checkout, form wizards, async document processing):
- Generate a Mermaid `stateDiagram-v2`.
- Explicitly define valid transitions between states: `Idle`, `Loading`, `Validating`, `Success`, `Error`, and `Rollback`.
- Detail guard conditions required to transition between steps.

### 5. Edge-Case, Interruption & Error Flows
- **Network Loss:** Offline banners, optimistic state preservation, and automatic retry upon reconnect.
- **Session Expiry:** Graceful token refresh or re-authentication modal that preserves the user's uncommitted form state.
- **Unsaved Changes Guard:** Browser navigation interception warning the user before discarding modifications.
- **Empty & Error States:** Explicit recovery buttons leading back to safe screens (e.g. "Return to Dashboard").

### 6. Deep Linking & History Management
- Canonical URL specifications for all views and modals.
- Browser History Stack expectations: which modals mutate the URL (`?modal=export`) and how the browser back button behaves.

## Rules & Constraints
- No dead ends: every screen must have at least one unambiguous exit path or back navigation.
- Every state transition must explicitly define its trigger (user event, timer, or webhook/SSE event).
- Never ignore interrupted states (e.g., user navigating away midway through a multi-step form).

## Rationalization Table
| Temptation / Shortcut | Reality |
| :--- | :--- |
| "Developers can figure out navigation from screen mockups." | Static screens hide conditional logic, modal states, and back-button behavior. |
| "Error and 404 screens can be added at the end." | Untracked error paths lead to blank screens and broken user experiences. |
| "A single happy-path flowchart is sufficient." | Real users encounter expired sessions, lost connections, and permission denials. |

