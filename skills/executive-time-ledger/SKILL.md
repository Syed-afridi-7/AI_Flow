---
name: executive-time-ledger
description: Use when conducting founder calendar audits, tracking high-leverage vs low-leverage executive time allocation, enforcing energy management boundaries, optimizing deep work blocks, and auditing weekly operational throughput.
---

# Executive Time Ledger

## Overview
Serves as an executive operating system and calendar audit engine for founders, technical leaders, and executives. Analyzes actual calendar utilization against the Andy Grove High-Output Management leverage tiers ($10k/hr vs $10/hr tasks), measures context switching penalties (attention residue), protects uninterrupted 3-to-4-hour deep work blocks, and designs defensive weekly schedules to maximize organizational leverage.

## When to Use
- **Trigger symptoms:** When a founder or tech lead feels overwhelmed by meeting sprawl, experiences chronic context switching, struggles to find uninterrupted coding/strategy time, needs to delegate operational tasks, or wants to audit weekly executive time distribution.
- **When NOT to use:** Routine team sprint task tracking (use Jira/Linear workflows), personal pomodoro timers, or micro-managing employee hourly timesheets.

## Instructions

Execute the executive time audit and schedule optimization across four phases:

### Phase 1: Calendar & Activity Ingestion
1. **Log Activity Entries:** Collect 1–2 weeks of actual calendar entries, meetings, ad-hoc interruptions, and slack/email management blocks.
2. **Capture Metadata per Block:**
   - Duration (minutes) and start/end time.
   - Meeting type (1-on-1, team sync, client pitch, board meeting, external vendor).
   - Attendee count and whether the executive is the driver, active contributor, or passive listener.
   - Level of preparation required (zero, 15m review, multi-hour slide deck prep).

### Phase 2: Leverage Tier & Energy Categorization
Classify every activity block into the Grove Leverage Framework:
1. **Tier 1: $10,000/hr Activities (Highest Strategic Moat):**
   - Core product architecture, key executive hiring, major enterprise deals, fundraising, capital allocation, setting company strategy.
2. **Tier 2: $1,000/hr Activities (High Leverage Execution):**
   - Product roadmap prioritization, critical technical reviews, high-value client presentations, strategic partner integrations.
3. **Tier 3: $100/hr Activities (Necessary Operational Overhead):**
   - Routine team standups, customer support escalations, reviewing standard pull requests, vendor negotiations.
4. **Tier 4: $10/hr Activities (Delegation & Automation Targets):**
   - Meeting scheduling, administrative data entry, filing expenses, ad-hoc status queries.

### Phase 3: Fragmentation & Attention Residue Diagnosis
1. **Compute Deep Work vs Fragmented Time:**
   - Calculate continuous blocks &ge; 120 minutes with zero scheduled interruptions.
   - Flag "Swiss cheese" days with 30-minute gaps between meetings where meaningful deep work is impossible.
2. **Calculate Context Switching Penalty:**
   - Quantify daily context shifts across disparate cognitive domains (e.g., switching from deep Rust coding to a marketing sync to an investor pitch within 90 minutes).
3. **Audit Meeting Utility:**
   - Flag any meeting lacking a written agenda or pre-read document.
   - Identify meetings where the executive is a passive attendee and can be replaced with an asynchronous digest.

### Phase 4: Ideal Schedule Architecture & Defensive Protocols
1. **Architect the Ideal Week (Theme-Based Scheduling):**
   - **Maker Mornings:** Daily 3–4 hour uninterrupted focus blocks (8:30 AM – 12:30 PM) protected for Tier 1 deep work.
   - **Manager Afternoons:** Consolidated meeting slots (1:30 PM – 5:00 PM) batching 1-on-1s and external calls.
   - **Focus Days:** At least 2 full days per week designated as meeting-free (e.g., Focus Tuesdays & Thursdays).
2. **Implement Defensive Boundary Rules:**
   - "No Agenda, No Meeting" cancellation rule.
   - Default meeting durations: shift 30m &rarr; 20m; shift 60m &rarr; 45m.
   - Async-first status updates via Loom or written briefs.
   - Executive Assistant / AI automation delegation checklist for all Tier 4 activities.

## Rules & Constraints
- **Minimum 40% Deep Work Target:** At least 40% of the executive's weekly working hours must be allocated to uninterrupted Tier 1 and Tier 2 strategic work.
- **Consolidated Meeting Blocks:** Meetings must be clustered contiguously into afternoon batches rather than scattered across the day.
- **Asynchronous Default:** Status reporting meetings without active decision-making must be converted into written or recorded asynchronous updates.
- **Weekly Reconciliation:** Conduct a weekly Friday retro reconciling planned vs actual time allocation.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Correction |
| :--- | :--- |
| Scattering meetings throughout the morning | Protect morning hours exclusively for uninterrupted deep work. |
| Attending meetings as a passive observer | Request an asynchronous summary or recording instead. |
| Scheduling 60-minute meetings by default | Default to 20 or 45-minute meetings to preserve transition buffers. |
| Doing administrative scheduling manually | Delegate to an EA or configure calendar scheduling links with strict rule gates. |
