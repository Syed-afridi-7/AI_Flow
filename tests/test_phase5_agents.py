import unittest
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
import engine.agents.phase5_api_data_perf # Registers Phase 5 agents


class TestPhase5Agents(unittest.TestCase):
    def setUp(self):
        self.runner = DualAgentRunner()

    def test_phase5_skills_registered(self):
        phase5_skills = [
            "api-contract-generator",
            "db-migration-optimizer",
            "performance-profiling"
        ]
        all_skills = AgentRegistry.list_skills()
        for skill in phase5_skills:
            self.assertIn(skill, all_skills, f"Skill {skill} should be registered")

    def test_api_contract_generator_run(self):
        result, scorecard = self.runner.run_skill(
            "api-contract-generator",
            prompt="User authentication and profile management endpoints"
        )
        self.assertIn("openapi: 3.1.0", result.content)
        self.assertIn("RFC 7807", result.content)
        self.assertTrue(scorecard.passed)

    def test_db_migration_optimizer_run(self):
        result, scorecard = self.runner.run_skill(
            "db-migration-optimizer",
            prompt="Add email_verified column and composite index to users table"
        )
        self.assertIn("CONCURRENTLY", result.content)
        self.assertIn("Zero-Downtime", result.content)
        self.assertTrue(scorecard.passed)

    def test_performance_profiling_run(self):
        result, scorecard = self.runner.run_skill(
            "performance-profiling",
            prompt="Optimize slow dashboard initial load, LCP 4.2s, memory leak in chart component"
        )
        self.assertIn("Core Web Vitals", result.content)
        self.assertIn("LCP", result.content)
        self.assertTrue(scorecard.passed)


if __name__ == "__main__":
    unittest.main()
