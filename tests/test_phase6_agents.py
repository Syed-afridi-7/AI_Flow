import unittest
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
import engine.agents.phase6_devops_finops # Registers Phase 6 agents


class TestPhase6Agents(unittest.TestCase):
    def setUp(self):
        self.runner = DualAgentRunner()

    def test_phase6_skills_registered(self):
        phase6_skills = [
            "devops-docker-deploy",
            "ci-cd-pipeline-builder",
            "finops-token-optimizer"
        ]
        all_skills = AgentRegistry.list_skills()
        for skill in phase6_skills:
            self.assertIn(skill, all_skills, f"Skill {skill} should be registered")

    def test_devops_docker_deploy_run(self):
        result, scorecard = self.runner.run_skill(
            "devops-docker-deploy",
            prompt="Production multi-stage Dockerfile for FastAPI backend with non-root user"
        )
        self.assertIn("USER appuser", result.content)
        self.assertIn("HEALTHCHECK", result.content)
        self.assertTrue(scorecard.passed)

    def test_ci_cd_pipeline_builder_run(self):
        result, scorecard = self.runner.run_skill(
            "ci-cd-pipeline-builder",
            prompt="GitHub Actions workflow for testing, linting, and secure deployment"
        )
        self.assertIn("permissions:", result.content)
        self.assertIn("actions/checkout@", result.content)
        self.assertTrue(scorecard.passed)

    def test_finops_token_optimizer_run(self):
        result, scorecard = self.runner.run_skill(
            "finops-token-optimizer",
            prompt="Optimize LLM context usage, static prefix caching, and prompt compression"
        )
        self.assertIn("Prompt Caching", result.content)
        self.assertIn("Token Reduction", result.content)
        self.assertTrue(scorecard.passed)


if __name__ == "__main__":
    unittest.main()
