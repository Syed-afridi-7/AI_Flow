from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from engine.core.types import Blocker, GenerationResult, TaskContext, ValidationScorecard

if TYPE_CHECKING:
    from engine.model.synthesizer import NeuroSymbolicSynthesizer


class BaseAgent(ABC):
    """Base class for all algorithmic agents."""

    def __init__(self, name: str, skill_name: str, role: str):
        self.name = name
        self.skill_name = skill_name
        self.role = role

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} skill={self.skill_name} role={self.role}>"


class BaseGenerator(BaseAgent):
    """Base class for all Generator (Persona A) agents."""

    def __init__(
        self,
        name: str,
        skill_name: str,
        role: str,
        synthesizer: NeuroSymbolicSynthesizer | None = None,
    ):
        super().__init__(name, skill_name, role)
        self.synthesizer = synthesizer

    def synthesize_context(self, prompt: str, domain: str = "") -> list[Any]:
        """Retrieve semantic context from synthesizer if available, else empty list."""
        if self.synthesizer is not None:
            return self.synthesizer.synthesize_context(prompt, domain=domain)
        return []

    @abstractmethod
    def generate(self, context: TaskContext) -> GenerationResult:
        """Synthesize the deliverable deterministically based on context."""
        pass

    def refine(self, context: TaskContext, previous: GenerationResult, blockers: list[Blocker]) -> GenerationResult:
        """Self-correct programmatic violations identified by the Validator."""
        if self.synthesizer is not None and blockers:
            repaired_content = self.synthesizer.repair(previous.content, blockers)
            return GenerationResult(
                skill_name=self.skill_name,
                content=repaired_content,
                metadata=dict(previous.metadata) if previous.metadata else {},
            )
        return self.generate(context)


class BaseValidator(BaseAgent):
    """Base class for all Validator (Persona B) agents."""

    @abstractmethod
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        """Run AST parsing, security scans, and rubric scoring against the deliverable."""
        pass
