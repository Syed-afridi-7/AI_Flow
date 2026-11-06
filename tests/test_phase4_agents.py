import unittest
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
import engine.agents.phase4_design_frontend # Registers Phase 4 agents


class TestPhase4Agents(unittest.TestCase):
    def setUp(self):
        self.runner = DualAgentRunner()

    def test_phase4_skills_registered(self):
        phase4_skills = [
            "design-system-tokens",
            "landing-page-converter",
            "accessibility-wcag-audit"
        ]
        all_skills = AgentRegistry.list_skills()
        for skill in phase4_skills:
            self.assertIn(skill, all_skills, f"Skill {skill} should be registered")

    def test_design_system_tokens_run(self):
        result, scorecard = self.runner.run_skill(
            "design-system-tokens",
            prompt="Fintech dashboard dark mode palette with emerald accent"
        )
        self.assertIn("--color-", result.content)
        self.assertIn("dark", result.content.lower())
        self.assertTrue(scorecard.passed)

    def test_landing_page_converter_run(self):
        result, scorecard = self.runner.run_skill(
            "landing-page-converter",
            prompt="B2B AI API monitoring tool for engineering teams"
        )
        self.assertIn("Hero Value Proposition", result.content)
        self.assertIn("Call to Action", result.content)
        self.assertTrue(scorecard.passed)

    def test_accessibility_wcag_audit_run(self):
        result, scorecard = self.runner.run_skill(
            "accessibility-wcag-audit",
            prompt="Audit modal dialog and keyboard navigation traps"
        )
        self.assertIn("WCAG", result.content)
        self.assertIn("ARIA", result.content)
        self.assertTrue(scorecard.passed)


if __name__ == "__main__":
    unittest.main()
