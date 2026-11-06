---
name: freelance-client-onboarding
description: Use when onboarding a new freelance or agency client, scoping project requirements, drafting statements of work (SOW) and proposals, establishing communication protocols, managing discovery intake, and setting up client access provisioning.
---

# Freelance Client Onboarding

## Overview
The **Freelance Client Onboarding** skill establishes an end-to-end operational framework for converting prospective client inquiries into structured, legally protected, and aligned engagements. It standardizes client discovery intake, Statements of Work (SOW), project milestones, communication boundaries, revision policies, payment schedules, and secure access provisioning. By defining strict boundaries before development begins, this skill eliminates scope creep, unpaid discovery, ghosting delays, and misaligned expectations.

## When to Use
- **Trigger symptoms:** When signing a new consulting or development client, scoping project requirements, drafting an SOW or freelance proposal, defining project deliverables, establishing communication and revision boundaries, or orchestrating environment access handshakes.
- **When NOT to use:** Routine bug fixes within an active, established contract, internal product development with no external client, or automated billing reconciliation tasks (use `invoice-billing-tracker`).

## Instructions

Execute client onboarding through five standardized operational phases:

### Phase 1: Client Discovery & Intake Diagnosis
1. **Business Objective Extraction:** Identify the client's core metric, business goal, and target launch deadline. Determine the designated single sign-off stakeholder.
2. **Technical Scope Audit:** Ingest requirements, existing codebases, infrastructure dependencies, third-party integrations, and design assets.
3. **Budget & Constraints Alignment:** Confirm project model: Fixed-Price Milestone, Dedicated Monthly Retainer, or Capped Time-and-Materials. Identify client dependencies and external blockers.

### Phase 2: Statement of Work (SOW) & Proposal Construction
1. **Explicit Deliverable Inventory:** Itemize every tangible deliverable with objective acceptance criteria.
2. **Explicit Out-of-Scope Exclusions:** Document every adjacent feature, uncommitted integration, maintenance service, or ongoing support item that is explicitly excluded.
3. **Revision Mechanics:** Institute a strict cap on revision rounds (maximum 2 rounds per milestone) with a formal Change Order procedure for extra work.
4. **Approval Windows:** Define a 5-to-7 business day acceptance review window with an automatic "silence-is-acceptance" clause to prevent project stall.

### Phase 3: Commercial Terms, Payment & IP Protection
1. **Deposit Gate:** Enforce a non-negotiable upfront deposit (30% to 50%) prior to scheduling or commencing any billable work.
2. **Milestone Schedule:** Tie subsequent payments to objective deliverable handoffs rather than arbitrary calendar dates.
3. **Intellectual Property Transfer:** Explicitly mandate that copyright and intellectual property rights remain with the contractor until the final invoice is paid in 100% full.
4. **Late Payment Penalties:** Specify net-14 payment terms, a 1.5% monthly late fee, and an immediate right to suspend work upon overdue invoices.

### Phase 4: Communication Governance & SLA Boundaries
1. **Channel Policy:** Direct all project communications to a single asynchronous channel (Slack Connect or dedicated email thread). Exclude personal SMS, WhatsApp, and unscheduled voice calls.
2. **Response SLAs:** Define explicit communication response times (e.g., 24 business hours). Document non-working hours and weekend blackouts.
3. **Weekly Status Cadence:** Mandate a weekly asynchronous progress memo summarizing completed items, active blockers, and upcoming milestones.

### Phase 5: Access Provisioning & Kickoff Operations
1. **Zero-Trust Credential Exchange:** Require credentials, API keys, and repository invitations to be shared via encrypted password managers (Bitwarden, 1Password) or platform-native RBAC, never raw in chat.
2. **Staging & Production Guardrails:** Establish development and staging environments. Never test or develop directly in client production environments.
3. **Kickoff Meeting Protocol:** Conduct a focused 45-minute kickoff meeting to align on milestones, verify access permissions, and lock in the immediate Sprint 1 deliverables.

## Rules & Constraints
- **Never Work Without a Deposit:** No discovery sessions, system architectures, or code commits begin before the upfront deposit clears.
- **Strict Out-of-Scope Listing:** Every proposal must have an unambiguous "Out of Scope" section; silence on an exclusion does not mean it is excluded.
- **IP Retention Shield:** Intellectual property does not transfer incrementally; transfer occurs solely upon complete contract payment reconciliation.
- **Single Approver Mandate:** The client must designate one point of contact with binding decision-making authority to avoid contradictory multi-stakeholder feedback.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Operational Correction |
| :--- | :--- |
| Starting work on verbal agreement or "PO coming soon" | Enforce signed SOW and cleared deposit as non-negotiable work gates. |
| Vague deliverables like "Build modern web platform" | Provide itemized functional specs with testable acceptance criteria. |
| Unlimited revisions included in fixed fee | Limit to 2 revisions per milestone; require Change Order for extras. |
| Exchanging database credentials in plain text chat | Require encrypted password vaults or direct invitation to client teams. |
| Multi-stakeholder conflicting feedback loops | Contractually require a single Client Project Lead for unified sign-offs. |
