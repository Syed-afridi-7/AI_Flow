App Flow & Navigation Architecture

You are a Principal Product Designer & Frontend Architect. Using the PRD and UI/UX design brief, map out the comprehensive application navigational flow, state transitions, and interaction pathways before frontend development.

Product / Feature Context: [PASTE PRD, SCREENS, OR FEATURE DESCRIPTION]

Deliver the App Flow with these exact sections:

1. High-Level Navigation Map (Mermaid Diagram):
   - Mermaid flowchart (`flowchart TD`) showing all top-level routes, navigation stacks, and modal hierarchies.

2. Screen-to-Screen State Transitions:
   - For every screen:
     - Entry points (routes, deep links, push notifications)
     - User trigger actions (buttons, gestures, keystrokes)
     - Resulting state transition and target screen
     - Shared transition context / URL parameters passed

3. Decision Trees & Conditional Branching:
   - Authentication gates (Public vs Protected routes, onboarding completion checks)
   - Role-Based view access (Admin vs Member vs Guest views)
   - Feature flags and experimental branches

4. State Machine Architecture (Mermaid State Diagram):
   - Formal `stateDiagram-v2` for core complex workflows (e.g. multi-step checkout, authentication lifecycle, form wizards)
   - Explicit States: Idle, Validating, Submitting, Success, Error, Offline

5. Edge-Case, Interruption & Failure Flows:
   - Network failure / offline state handling and reconnection recovery
   - Session timeout / 401 refresh token flow during active user action
   - Unsaved changes confirmation dialogs on route leave
   - 404 Not Found and 500 Server Error fallback screens

6. Deep Linking & URL Hierarchy:
   - Canonical URL structures, query parameters, and browser back/forward history behavior

Be exhaustive. Map every path an end user can take, leaving no dead ends or untracked transition states.

