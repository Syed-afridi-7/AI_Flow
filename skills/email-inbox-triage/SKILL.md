---
name: email-inbox-triage
description: Use when classifying inbound client emails, detecting urgent requests, prioritizing inbox traffic, extracting actionable tasks into project trackers, and generating professional, tone-calibrated response drafts.
---

# Email Inbox Triage

## Overview
The **Email Inbox Triage** skill provides an automated, high-precision processing framework for incoming client, prospect, and business correspondence. It systematically parses raw email threads, classifies messages into a standardized 6-tier priority taxonomy (P0 Critical Emergency down to P5 Spam/Trash), detects underlying urgency and sentiment, extracts structured action items with deadlines, and generates professional, tone-calibrated draft replies that protect boundaries while maintaining high-trust client relationships.

## When to Use
- **Trigger symptoms:** When processing unread email queues, triaging customer or client inquiries in background daemons, extracting action items and task tickets from client messages, drafting diplomatic responses to demanding stakeholders, or detecting informal scope creep disguised as quick email requests.
- **When NOT to use:** Outbound bulk cold-email marketing campaigns, automated marketing newsletter generation, or internal real-time chat moderation.

## Instructions

Execute the email triage process through five structured operational phases:

### Phase 1: Inbound Message Parsing & Intent Classification
1. **Metadata Ingestion:** Extract sender address, recipient list, CC/BCC stakeholders, subject line, timestamp, and message thread history.
2. **Intent & Priority Classification:** Assign the message to one of six mutually exclusive priority categories:
   - **P0 - Critical Emergency:** Production downtime, security breaches, broken checkout flows, severe revenue-impacting bugs. Requires immediate escalation and draft response within 1 hour.
   - **P1 - Active Milestone & Deliverables:** Client feedback on active SOW deliverables, review approvals, required asset handoffs, scheduled sync confirmations. Requires same-day response (within 8 business hours).
   - **P2 - New Business & Inbound Opportunity:** Prospective client inquiries, RFP requests, consulting leads, partnership proposals. Requires response within 24 business hours.
   - **P3 - Administrative & Financial Operations:** Invoice inquiries, payment receipts, tax documents, contract signatures, vendor billing questions. Handled within standard accounting cycles (24-48 business hours).
   - **P4 - Low-Priority Informational / FYI:** Automated build alerts, product newsletters, community updates, non-actionable CC notifications. No response required; tag and file.
   - **P5 - Unsolicited Commercial & Spam:** Unsolicited sales pitches, automated phishing, irrelevant marketing blasts. Archive or delete immediately.

### Phase 2: Sentiment & Risk Detection
1. **Tone & Emotion Analysis:** Assess sender sentiment (Affirmative, Neutral, Inquisitive, Frustrated, Panicked, or Adversarial).
2. **Scope Creep Scanner:** Flag phrases attempting informal scope expansion (e.g., "While you're in there", "Could you also quickly tweak", "Just one small additional page").
3. **Budget & Commercial Signals:** Identify mentions of payment disputes, budget holds, or contract modifications.

### Phase 3: Action Item & Task Extraction
1. **Itemized Tasks:** Extract every explicit and implicit action item required of the recipient, specifying the task title, context, estimated complexity, and suggested due date.
2. **Client Commitments:** Note any promises or deliverables the sender committed to provide, creating client tracking reminders.
3. **Deadlines & Constraints:** Extract hard deadlines mentioned in the text (e.g., "Need this for board meeting on Thursday 2 PM EST").

### Phase 4: Tone-Calibrated Draft Response Generation
1. **Response Stance Selection:** Choose appropriate communication posture:
   - *Executive / Direct:* For senior stakeholders; concise, bulleted, action-oriented.
   - *Warm Professional:* For routine active client communications and milestone reviews.
   - *Firm Boundary Defense:* For scope creep or unrealistic deadline requests; politely acknowledges the idea and attaches a Change Order estimation requirement.
   - *Empathetic De-escalation:* For frustrated clients facing technical blockers; validates concern, presents concrete resolution steps, and sets realistic timeframes.
2. **Draft Rules:** Never apologize reflexively for contractual boundaries; never promise unrealistic same-day turnaround for non-emergency requests; always end with a single clear Call-to-Action (CTA).

### Phase 5: Task Queue Handoff & Dispatch
1. Output structured JSON matching project tracker formats (Linear, GitHub Issues, Asana) for direct API dispatch or daemon queuing.
2. Store draft responses in the designated staging area (e.g., `output/email_drafts/`) for human review prior to sending.

## Rules & Constraints
- **Zero Hallucinated Commitments:** Drafts must NEVER commit to delivery dates or feature implementations without explicit project tracker verification.
- **Scope Creep Quarantine:** Informal feature requests in email threads must be routed to the formal Change Order process, never quietly absorbed into active deliverables.
- **Sensitive Information Redaction:** Inbound emails containing raw passwords, API keys, or financial account details must be flagged for redaction and secure rotation.
- **Strict Anti-Sycophancy:** Responses must remain courteous, authoritative, and professional without using subservient, overly apologetic phrasing.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Operational Correction |
| :--- | :--- |
| Apologizing repeatedly for normal business hour response delays | State standard working hours and deliver the requested answer directly. |
| Treating every client email with the word "urgent" as a P0 | Evaluate actual production impact; reserve P0 strictly for true outages. |
| Silently absorbing "quick extra requests" into active work | Politely acknowledge the request and offer to scope it via Change Order. |
| Writing long, unstructured essay replies | Use executive bullet points, bold key dates, and provide a single clear next step. |
| Committing to arbitrary deadlines in draft replies | Offer realistic milestone estimates tied to active sprint priorities. |
