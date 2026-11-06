import unittest
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
import engine.agents.phase7_freelance_ops # Registers Phase 7 agents


class TestPhase7Agents(unittest.TestCase):
    def setUp(self):
        self.runner = DualAgentRunner()

    def test_phase7_skills_registered(self):
        phase7_skills = [
            "freelance-client-onboarding",
            "email-inbox-triage",
            "invoice-billing-tracker"
        ]
        all_skills = AgentRegistry.list_skills()
        for skill in phase7_skills:
            self.assertIn(skill, all_skills, f"Skill {skill} should be registered")

    def test_freelance_client_onboarding_run(self):
        result, scorecard = self.runner.run_skill(
            "freelance-client-onboarding",
            prompt="Full-stack web application development for ACME Corp, budget $15,000"
        )
        self.assertIn("Statement of Work", result.content)
        self.assertIn("Milestone Billing Schedule", result.content)
        self.assertTrue(scorecard.passed)

    def test_email_inbox_triage_run(self):
        result, scorecard = self.runner.run_skill(
            "email-inbox-triage",
            prompt="From: client@acme.com. Need urgent fix on billing page before investor meeting tomorrow."
        )
        self.assertIn("Priority", result.content)
        self.assertIn("Draft Response", result.content)
        self.assertTrue(scorecard.passed)

    def test_invoice_billing_tracker_run(self):
        result, scorecard = self.runner.run_skill(
            "invoice-billing-tracker",
            prompt="Generate milestone invoice for Sprint 1 delivery, $5,000 due in 15 days"
        )
        self.assertIn("INVOICE", result.content)
        self.assertIn("Accounts Receivable Aging", result.content)
        self.assertTrue(scorecard.passed)


if __name__ == "__main__":
    unittest.main()
