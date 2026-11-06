from engine.core.base import BaseGenerator, BaseValidator
from engine.core.registry import AgentRegistry
from engine.core.types import TaskContext, GenerationResult, ValidationScorecard, Blocker, Severity


# ============================================================================
# 1. Freelance Client Onboarding
# ============================================================================
class SowProposalWriter(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# Statement of Work (SOW) & Project Proposal

## 1. Project Overview & Deliverables
**Client Engagement:** {context.prompt}

## 2. Scope Matrix & Boundaries
- **In-Scope:** Architecture design, full-stack implementation, automated unit testing, deployment setup.
- **Out-of-Scope:** Ongoing content marketing, 24/7 dedicated telephone support, unbudgeted feature additions.
- **Revision Limits:** All milestones include up to two (2) consolidated rounds of feedback. Additional revisions billed at standard hourly rate.

## 3. Milestone Billing Schedule
| Milestone | Deliverable Scope | Payment % | Amount |
| :--- | :--- | :--- | :--- |
| **Milestone 1** | Project Kickoff & Architecture Spec | 40% (Upfront) | Invoiced upon contract signing |
| **Milestone 2** | Core Backend & UI Integration | 30% | Invoiced upon staging demo |
| **Milestone 3** | Final Verification & Production Handover | 30% | Invoiced upon release sign-off |

## 4. Intellectual Property & Terms
Full intellectual property transfer occurs immediately upon receipt of 100% final milestone payment.
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class ContractScopeAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "Statement of Work" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="SOW_NO_HEADER", message="Must include Statement of Work specification."))
        if "Milestone Billing Schedule" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="SOW_NO_MILESTONES", message="Must include Milestone Billing Schedule."))
        if "Revision Limits" not in result.content:
            score -= 20
            blockers.append(Blocker(rule_id="SOW_NO_REVISIONS", message="Must protect against scope creep with revision limits."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"scope": 50, "billing": 50},
            blockers=blockers,
            audit_summary="Client proposal and SOW approved." if score >= 85 else "SOW missing milestones or revision limits."
        )


# ============================================================================
# 2. Email Inbox Triage
# ============================================================================
class InboundInquiryClassifier(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# Email Triage & Draft Response

## 1. Classification & Priority
- **Inbound Message:** {context.prompt}
- **Assigned Priority:** P1 (High Priority - Action required within 4 business hours)
- **Category:** Client Operational Request

## 2. Extracted Action Items
1. Review billing page transaction flows and verify error bounds.
2. Confirm fix in staging environment before tomorrow's meeting.
3. Reply to client with status update and timeline commitment.

## 3. Professional Draft Response (Review & Approve Before Sending)
> Subject: Re: Urgent update - Billing verification
>
> Hi there,
>
> Thanks for flagging this. I have received your request regarding the billing page and am currently investigating the transaction flow in our staging environment.
>
> We will have the fix verified and deployed well ahead of your investor meeting tomorrow. I will send you a confirmation link as soon as testing is complete.
>
> Best regards,  
> Engineering Lead
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class ClientCommunicationsDrafter(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "Priority" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="EMAIL_NO_PRIORITY", message="Must assign priority classification (e.g. P1)."))
        if "Draft Response" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="EMAIL_NO_DRAFT", message="Must provide a professional draft response."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"triage": 50, "draft": 50},
            blockers=blockers,
            audit_summary="Email triage approved." if score >= 85 else "Missing priority or draft response."
        )


# ============================================================================
# 3. Invoice Billing Tracker
# ============================================================================
class MilestoneInvoiceGenerator(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# INVOICE & BILLING SUMMARY

## 1. Invoice Document
**Invoice #:** INV-2026-0042  
**Date of Issue:** 2026-11-06  
**Payment Due Date:** 2026-11-21 (Net 15)  
**Client:** ACME Corp  

### Itemized Billing Breakdown
| Item / Milestone Description | Hours / Units | Rate | Total |
| :--- | :--- | :--- | :--- |
| {context.prompt} | 1 Milestone | $5,000.00 | $5,000.00 |
| **Total Balance Due:** | | | **$5,000.00** |

## 2. Payment Details
- **ACH / Wire Routing:** Bank of America | Routing: `123456789` | Account: `9876543210`
- **Crypto / USDC:** `0x71C...49A1` (ERC-20)

## 3. Accounts Receivable Aging & Reminders
- **Status:** 0–30 Days (Current)
- **Automated Dunning Schedule:**
  - Day 12: Polite reminder prior to due date.
  - Day 16: First overdue notice if payment unreconciled.
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class LedgerReconciliationAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "INVOICE" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="INVOICE_NO_HEADER", message="Must include itemized INVOICE document."))
        if "Accounts Receivable Aging" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="INVOICE_NO_AGING", message="Must track accounts receivable aging."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"invoice": 50, "aging": 50},
            blockers=blockers,
            audit_summary="Invoice tracker approved." if score >= 85 else "Missing invoice or aging schedule."
        )


# ============================================================================
# Register All Phase 7 Skills
# ============================================================================
AgentRegistry.register("freelance-client-onboarding", SowProposalWriter, ContractScopeAuditor)
AgentRegistry.register("email-inbox-triage", InboundInquiryClassifier, ClientCommunicationsDrafter)
AgentRegistry.register("invoice-billing-tracker", MilestoneInvoiceGenerator, LedgerReconciliationAuditor)
