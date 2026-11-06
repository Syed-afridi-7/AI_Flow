---
name: invoice-billing-tracker
description: Use when tracking billable freelance hours, generating milestone and recurring retainer invoices, managing accounts receivable aging, calculating late payment penalties, drafting payment reminder notices, and reconciling client ledgers.
---

# Invoice Billing Tracker

## Overview
The **Invoice Billing Tracker** skill provides a complete financial management and accounts receivable operations framework for independent contractors, freelance software engineers, and boutique consulting agencies. It automates the generation of compliant, audit-ready milestone and retainer invoices, tracks billable hours against contractual caps, monitors payment aging buckets (Current, 1-15 days, 16-30 days, 31-60 days, 60+ days delinquent), applies statutory late fee interest, drafts escalating dunning reminder sequences, and reconciles financial ledgers for business health transparency.

## When to Use
- **Trigger symptoms:** When completing project milestones requiring invoicing, billing recurring monthly retainers, compiling weekly billable timesheets against client budgets, auditing accounts receivable aging, calculating accrued late fees on overdue balances, or composing multi-stage payment reminders.
- **When NOT to use:** Double-entry corporate general ledger accounting (e.g., enterprise SAP/NetSuite setups), employee payroll calculation (W-2 withholding), or personal consumer expense tracking.

## Instructions

Execute billing and receivables tracking through five standardized operational phases:

### Phase 1: Timesheet & Deliverable Audit
1. **Contractual Budget Verification:** Audit logged hours or milestone deliverables against the signed Statement of Work (SOW). Verify that total logged units do not exceed agreed contractual caps.
2. **Acceptance Verification:** Confirm that milestone deliverables have met objective acceptance criteria or cleared the 5-day silence-is-acceptance review window before billing.
3. **Expense & Reimbursables Reconciliation:** Compile approved pass-through expenses (third-party cloud hosting, specialized API credits, licensed software fonts) with attached proof of payment.

### Phase 2: Invoice Construction & Tax Compliance
1. **Sequential Invoice Identification:** Assign unique, sequential invoice identifiers following a structured format (e.g., `INV-YYYY-XXXX`).
2. **Entity & Tax Metadata:** Specify legal entity details for both vendor and client: registered corporate names, billing addresses, tax identification numbers (EIN, VAT, GST), and purchase order (PO) numbers.
3. **Itemized Billing Lines:** Structure line items with unambiguous descriptions, service delivery dates, units/hours, unit rates, and extended totals.
4. **Remittance Instructions:** Provide clear payment instructions: domestic ACH routing/account numbers, international SWIFT/BIC/IBAN details, and secure online credit card payment links (Stripe/Wise).

### Phase 3: Accounts Receivable Aging & Ledger Logging
1. **Ledger Synchronization:** Record every issued invoice in the central financial ledger (JSON/CSV) with timestamp, invoice ID, client name, issue date, due date, amount, and payment status (`DRAFT`, `SENT`, `PAID`, `OVERDUE`, `DISPUTED`).
2. **Aging Bucket Segmentation:** Categorize outstanding invoices into aging tiers:
   - *Current:* Within agreed payment terms (Net-14 / Net-30).
   - *1-15 Days Past Due:* Grace period; first reminder triggered.
   - *16-30 Days Past Due:* Formal overdue status; late fee interest begins accruing.
   - *31-60 Days Past Due:* Delinquent; work paused, second escalation triggered.
   - *60+ Days Delinquent:* Critical default; collections / legal notice warning.

### Phase 4: Escalating Payment Reminders & Dunning Protocol
1. **Stage 1 (-3 Days to Due Date): Courtesy Notice:** Friendly, low-friction heads-up reminding the client of the upcoming invoice due date with attached PDF.
2. **Stage 2 (Due Date): Payment Due Notification:** Direct notification confirming the invoice is due today with remittance links.
3. **Stage 3 (+7 Days Overdue): First Late Notice:** Firm, polite reminder noting the overdue status and referencing contractual late interest terms.
4. **Stage 4 (+14 Days Overdue): Work Suspension & Late Fee Notice:** Formal notice applying accrued monthly late fee (1.5%), announcing immediate suspension of staging hosting and development work until payment clears.
5. **Stage 5 (+30 Days Overdue): Breach of Contract & Demand Letter:** Final demand for payment before initiating legal action or debt recovery.

### Phase 5: Payment Reconciliation & Financial Health Metrics
1. **Payment Settlement Logging:** Upon receipt of funds, log transaction IDs, settlement fees (Stripe/wire fees), net proceeds, and exact payment dates.
2. **Key Metric Calculations:** Calculate core freelance business metrics:
   - *Effective Hourly Rate (EHR):* Total gross project revenue divided by total actual hours invested.
   - *Days Sales Outstanding (DSO):* Average number of days required to collect payment after invoice issuance.
   - *Unbilled Work-in-Progress (WIP):* Accrued billable hours not yet invoiced.

## Rules & Constraints
- **Zero Arithmetic Discrepancies:** Line items, subtotals, tax/VAT calculations, discounts, and grand totals must reconcile to the exact cent without rounding errors.
- **Strict Budget Cap Enforcement:** Invoices must never exceed agreed contractual caps without an executed Change Order.
- **Explicit Payment Due Dates:** Every invoice must state an explicit calendar due date (e.g., `Due: November 20, 2026`), never ambiguous phrases like "payable upon receipt".
- **Contractual Work Suspension:** The right to pause development services upon 14 days of non-payment must be strictly exercised to limit financial exposure.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Operational Correction |
| :--- | :--- |
| Omitting bank remittance details on invoice PDF | Always embed full ACH, wire routing, and digital payment links on every invoice page. |
| Waiting 30 days after due date to send first reminder | Follow the 5-stage dunning cadence starting 3 days before due date. |
| Billing unapproved out-of-scope hours | Bill only contracted hours; route additional hours to approved Change Orders. |
| Inconsistent or non-sequential invoice numbering | Use standard sequential numbering (`INV-2026-0001`, `INV-2026-0002`). |
| Failing to specify tax exemption or VAT notes | Explicitly state VAT registration or "Reverse Charge: VAT to be accounted for by the recipient". |
