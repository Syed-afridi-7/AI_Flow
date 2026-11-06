from abc import ABC, abstractmethod
from engine.core.types import TaskContext, GenerationResult, ValidationScorecard, Blocker


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

    @abstractmethod
    def generate(self, context: TaskContext) -> GenerationResult:
        """Synthesize the deliverable deterministically based on context."""
        pass

    def refine(self, context: TaskContext, previous: GenerationResult, blockers: list[Blocker]) -> GenerationResult:
        """Self-correct programmatic violations identified by the Validator."""
        return self.generate(context)


class BaseValidator(BaseAgent):
    """Base class for all Validator (Persona B) agents."""

    @abstractmethod
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        """Run AST parsing, security scans, and rubric scoring against the deliverable."""
        pass
