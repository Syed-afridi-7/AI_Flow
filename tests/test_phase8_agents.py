import unittest
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
import engine.agents.phase8_growth_founder # Registers Phase 8 agents


class TestPhase8Agents(unittest.TestCase):
    def setUp(self):
        self.runner = DualAgentRunner()

    def test_phase8_skills_registered(self):
        phase8_skills = [
            "insta-reel-creator",
            "seo-content-strategist",
            "social-copy-repurposer",
            "executive-time-ledger"
        ]
        all_skills = AgentRegistry.list_skills()
        for skill in phase8_skills:
            self.assertIn(skill, all_skills, f"Skill {skill} should be registered")

    def test_insta_reel_creator_run(self):
        result, scorecard = self.runner.run_skill(
            "insta-reel-creator",
            prompt="How to build offline autonomous AI agents in pure Python"
        )
        self.assertIn("Hook", result.content)
        self.assertIn("Beat Sheet", result.content)
        self.assertTrue(scorecard.passed)
        self.assertGreaterEqual(scorecard.score, 85)

    def test_seo_content_strategist_run(self):
        result, scorecard = self.runner.run_skill(
            "seo-content-strategist",
            prompt="Topic cluster for python agent frameworks without external api"
        )
        self.assertIn("Search Intent", result.content)
        self.assertIn("Pillar-Cluster", result.content)
        self.assertTrue(scorecard.passed)

    def test_social_copy_repurposer_run(self):
        result, scorecard = self.runner.run_skill(
            "social-copy-repurposer",
            prompt="Turn our engineering devlog on AST-based validation into a technical Twitter thread and LinkedIn post"
        )
        self.assertIn("Twitter / X Thread", result.content)
        self.assertIn("LinkedIn", result.content)
        self.assertTrue(scorecard.passed)

    def test_executive_time_ledger_run(self):
        result, scorecard = self.runner.run_skill(
            "executive-time-ledger",
            prompt="Audit founder calendar: spent 4 hours on email triage, 2 hours on architecture, 1 hour on meetings"
        )
        self.assertIn("High-Leverage", result.content)
        self.assertIn("Delegation", result.content)
        self.assertTrue(scorecard.passed)


if __name__ == "__main__":
    unittest.main()
