import unittest
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
import engine.agents.phase3_release # Registers Phase 3 agents


class TestPhase3Agents(unittest.TestCase):
    def setUp(self):
        self.runner = DualAgentRunner()

    def test_phase3_skills_registered(self):
        phase3_skills = [
            "security-gap-audit",
            "dead-code-cleanup",
            "rigorous-code-review",
            "clean-git-commits"
        ]
        all_skills = AgentRegistry.list_skills()
        for skill in phase3_skills:
            self.assertIn(skill, all_skills, f"Skill {skill} should be registered")

    def test_security_gap_audit_run(self):
        result, scorecard = self.runner.run_skill(
            "security-gap-audit",
            prompt="Audit payment API gateway and webhook handler"
        )
        self.assertIn("Threat Vectors", result.content)
        self.assertIn("Remediation", result.content)
        self.assertTrue(scorecard.passed)

    def test_clean_git_commits_run(self):
        result, scorecard = self.runner.run_skill(
            "clean-git-commits",
            prompt="feat(auth): add OAuth2 provider verification"
        )
        self.assertIn("feat(", result.content)
        self.assertTrue(scorecard.passed)

    def test_dead_code_cleanup_run(self):
        result, scorecard = self.runner.run_skill(
            "dead-code-cleanup",
            prompt="Audit legacy auth helpers in src/utils/old_auth.py"
        )
        self.assertIn("Confidence", result.content)
        self.assertTrue(scorecard.passed)


if __name__ == "__main__":
    unittest.main()
