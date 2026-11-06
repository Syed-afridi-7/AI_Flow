import unittest
from engine.core.types import TaskContext, GenerationResult, ValidationScorecard, Blocker, Severity
from engine.core.base import BaseGenerator, BaseValidator
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner


class MockGenerator(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        return GenerationResult(skill_name=context.skill_name, content="v1: draft code")

    def refine(self, context: TaskContext, previous: GenerationResult, blockers: list[Blocker]) -> GenerationResult:
        return GenerationResult(skill_name=context.skill_name, content="v2: refined code addressing blockers")


class MockValidator(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        if "v1" in result.content:
            return ValidationScorecard(
                skill_name=result.skill_name,
                score=70,
                passed=False,
                blockers=[Blocker(rule_id="TEST_01", message="Incomplete implementation", severity=Severity.BLOCKER)],
                audit_summary="Failed due to v1 incomplete"
            )
        else:
            return ValidationScorecard(
                skill_name=result.skill_name,
                score=95,
                passed=True,
                blockers=[],
                audit_summary="Approved v2"
            )


class TestRunnerAndRegistry(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear()
        AgentRegistry.register("mock-skill", MockGenerator, MockValidator)

    def test_registry_registration(self):
        self.assertIn("mock-skill", AgentRegistry.list_skills())
        gen, val = AgentRegistry.get_agents("mock-skill")
        self.assertIsInstance(gen, MockGenerator)
        self.assertIsInstance(val, MockValidator)

    def test_single_mode_runner(self):
        runner = DualAgentRunner()
        result, scorecard = runner.run_skill("mock-skill", "Create test code", mode="single")
        self.assertEqual(result.content, "v1: draft code")
        self.assertTrue(scorecard.passed)
        self.assertEqual(scorecard.score, 100)

    def test_dual_mode_with_self_correction(self):
        runner = DualAgentRunner(max_refinements=2)
        result, scorecard = runner.run_skill("mock-skill", "Create test code", mode="dual")
        self.assertEqual(result.content, "v2: refined code addressing blockers")
        self.assertTrue(scorecard.passed)
        self.assertEqual(scorecard.score, 95)
        self.assertEqual(scorecard.iteration, 2)


if __name__ == "__main__":
    unittest.main()
