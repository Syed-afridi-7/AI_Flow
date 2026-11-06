import unittest
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
import engine.agents.phase2_execution # Registers Phase 2 agents


class TestPhase2Agents(unittest.TestCase):
    def setUp(self):
        self.runner = DualAgentRunner()

    def test_phase2_skills_registered(self):
        phase2_skills = ["task-to-skill", "playwright-e2e-testing", "systematic-debugging"]
        all_skills = AgentRegistry.list_skills()
        for skill in phase2_skills:
            self.assertIn(skill, all_skills, f"Skill {skill} should be registered")

    def test_task_to_skill_run(self):
        result, scorecard = self.runner.run_skill(
            "task-to-skill",
            prompt="Extract our database migration review workflow into a permanent skill"
        )
        self.assertIn("SKILL.md", result.content)
        self.assertIn("Workflow", result.content)
        self.assertTrue(scorecard.passed)

    def test_playwright_e2e_testing_run(self):
        result, scorecard = self.runner.run_skill(
            "playwright-e2e-testing",
            prompt="Test login flow, dashboard navigation, and settings save"
        )
        self.assertIn("test('", result.content)
        self.assertIn("storageState", result.content)
        self.assertTrue(scorecard.passed)

    def test_systematic_debugging_run(self):
        result, scorecard = self.runner.run_skill(
            "systematic-debugging",
            prompt="User sessions intermittently expire after 2 minutes instead of 2 hours"
        )
        self.assertIn("Hypothesis 1", result.content)
        self.assertIn("Root Cause", result.content)
        self.assertTrue(scorecard.passed)


if __name__ == "__main__":
    unittest.main()
