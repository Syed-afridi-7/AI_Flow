import unittest
from engine.core.types import Severity, Blocker, TaskContext, GenerationResult, ValidationScorecard
from engine.core.base import BaseAgent, BaseGenerator, BaseValidator

class TestCoreTypes(unittest.TestCase):
    def test_blocker_creation(self):
        blocker = Blocker(
            rule_id="SEC001",
            message="Hardcoded secret detected",
            severity=Severity.BLOCKER,
            line_number=42,
            remediation="Use environment variable"
        )
        self.assertEqual(blocker.rule_id, "SEC001")
        self.assertEqual(blocker.severity, Severity.BLOCKER)

    def test_task_context(self):
        ctx = TaskContext(skill_name="prd-generator", prompt="Build a CRM", inputs={"target": "B2B"})
        self.assertEqual(ctx.skill_name, "prd-generator")
        self.assertEqual(ctx.inputs["target"], "B2B")

    def test_validation_scorecard(self):
        sc = ValidationScorecard(
            skill_name="prd-generator",
            score=90,
            passed=True,
            category_scores={"completeness": 90},
            blockers=[],
            audit_summary="Approved"
        )
        self.assertTrue(sc.passed)
        self.assertEqual(sc.score, 90)

    def test_base_agent_subclassing(self):
        class DummyGen(BaseGenerator):
            def generate(self, context: TaskContext) -> GenerationResult:
                return GenerationResult(skill_name=context.skill_name, content="PRD Draft")

        class DummyVal(BaseValidator):
            def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
                return ValidationScorecard(skill_name=result.skill_name, score=95, passed=True)

        gen = DummyGen(name="DummyGen", skill_name="dummy", role="Generator")
        val = DummyVal(name="DummyVal", skill_name="dummy", role="Validator")
        
        ctx = TaskContext(skill_name="dummy", prompt="test")
        res = gen.generate(ctx)
        self.assertEqual(res.content, "PRD Draft")
        
        sc = val.audit(res, ctx)
        self.assertTrue(sc.passed)
        self.assertEqual(sc.score, 95)

if __name__ == "__main__":
    unittest.main()
