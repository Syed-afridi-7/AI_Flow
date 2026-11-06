from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Severity(str, Enum):
    BLOCKER = "blocker"
    WARNING = "warning"
    SUGGESTION = "suggestion"


@dataclass
class Blocker:
    rule_id: str
    message: str
    severity: Severity = Severity.BLOCKER
    line_number: Optional[int] = None
    remediation: Optional[str] = None


@dataclass
class TaskContext:
    skill_name: str
    prompt: str
    inputs: dict[str, Any] = field(default_factory=dict)
    workspace_path: Optional[str] = None
    target_files: list[str] = field(default_factory=list)


@dataclass
class GenerationResult:
    skill_name: str
    content: str
    files: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)


@dataclass
class ValidationScorecard:
    skill_name: str
    score: int
    passed: bool
    category_scores: dict[str, int] = field(default_factory=dict)
    blockers: list[Blocker] = field(default_factory=list)
    audit_summary: str = ""
    iteration: int = 1
