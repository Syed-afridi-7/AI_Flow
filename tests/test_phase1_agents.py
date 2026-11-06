import unittest
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
import engine.agents.phase1_architecture # Registers Phase 1 agents


class TestPhase1Agents(unittest.TestCase):
    def setUp(self):
        self.runner = DualAgentRunner()

    def test_phase1_skills_registered(self):
        phase1_skills = [
            "prd-generator",
            "trd-generator",
            "app-flow",
            "uiux-design-brief",
            "backend-schema",
            "system-architecture",
            "implementation-plan"
        ]
        all_skills = AgentRegistry.list_skills()
        for skill in phase1_skills:
            self.assertIn(skill, all_skills, f"Skill {skill} should be registered")

    def test_prd_generator_run(self):
        result, scorecard = self.runner.run_skill(
            "prd-generator",
            prompt="Build a SaaS billing and subscription portal"
        )
        self.assertIn("# Product Requirements Document", result.content)
        self.assertIn("User Stories", result.content)
        self.assertTrue(scorecard.passed)
        self.assertGreaterEqual(scorecard.score, 85)

    def test_backend_schema_run(self):
        result, scorecard = self.runner.run_skill(
            "backend-schema",
            prompt="E-commerce store with Users, Products, Orders, OrderItems"
        )
        self.assertIn("erDiagram", result.content)
        self.assertIn("CREATE TABLE", result.content)
        self.assertTrue(scorecard.passed)
        self.assertGreaterEqual(scorecard.score, 85)

    def test_trd_generator_run(self):
        result, scorecard = self.runner.run_skill(
            "trd-generator",
            prompt="High-throughput payment processing engine"
        )
        self.assertIn("p95", result.content)
        self.assertIn("SLA", result.content)
        self.assertTrue(scorecard.passed)
        self.assertGreaterEqual(scorecard.score, 85)


if __name__ == "__main__":
    unittest.main()
