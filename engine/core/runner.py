from typing import Optional, Any
from engine.core.types import TaskContext, GenerationResult, ValidationScorecard
from engine.core.registry import AgentRegistry


class DualAgentRunner:
    """Orchestrates the Dual-Agent Generator <-> Validator peer review and self-correction loop."""

    def __init__(self, max_refinements: int = 2):
        self.max_refinements = max_refinements

    def run_skill(
        self,
        skill_name: str,
        prompt: str,
        inputs: Optional[dict[str, Any]] = None,
        workspace_path: Optional[str] = None,
        target_files: Optional[list[str]] = None,
        mode: str = "dual"
    ) -> tuple[GenerationResult, ValidationScorecard]:
        """Execute a skill run in either 'single' or 'dual' mode."""
        generator, validator = AgentRegistry.get_agents(skill_name)
        context = TaskContext(
            skill_name=skill_name,
            prompt=prompt,
            inputs=inputs or {},
            workspace_path=workspace_path,
            target_files=target_files or []
        )

        # 1. Generator Initial Turn
        result = generator.generate(context)

        # If single mode requested, skip validation
        if mode == "single":
            scorecard = ValidationScorecard(
                skill_name=skill_name,
                score=100,
                passed=True,
                audit_summary="Single mode: validation skipped by user request.",
                iteration=1
            )
            return result, scorecard

        # 2. Validator Turn
        scorecard = validator.audit(result, context)
        iteration = 1

        # 3. Self-Correction Loop (if score < 85)
        while not scorecard.passed and iteration <= self.max_refinements:
            iteration += 1
            result = generator.refine(context, result, scorecard.blockers)
            scorecard = validator.audit(result, context)
            scorecard.iteration = iteration

        return result, scorecard
