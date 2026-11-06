from engine.core.base import BaseGenerator, BaseValidator
from engine.core.registry import AgentRegistry
from engine.core.types import TaskContext, GenerationResult, ValidationScorecard, Blocker, Severity


# ============================================================================
# 1. DevOps Docker Deploy
# ============================================================================
class ContainerizationEngineer(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# Production Multi-Stage Hardened Dockerfile
# Service: {context.prompt}

# ---------------------------------------------------------------------------
# Stage 1: Build & Dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Minimal Distroless / Hardened Runner
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

# Security: Create and switch to non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -u 10001 appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appgroup . .

ENV PATH=/home/appuser/.local/bin:$PATH \\
    PORT=8000

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class DockerSecurityAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "USER appuser" not in result.content and "USER 10001" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="DOCKER_ROOT_USER", message="Containers must run as a non-root user."))
        if "HEALTHCHECK" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="DOCKER_NO_HEALTHCHECK", message="Must define container HEALTHCHECK."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"security": 50, "health": 50},
            blockers=blockers,
            audit_summary="Docker security approved." if score >= 85 else "Docker image runs as root or lacks healthcheck."
        )


# ============================================================================
# 2. CI/CD Pipeline Builder
# ============================================================================
class ActionsArchitect(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""name: CI/CD Pipeline - {context.prompt}

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Security: Minimal top-level permissions
permissions:
  contents: read

concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Test Suite
        run: |
          python -m unittest discover -s tests -p "test_*.py"
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class PipelineSecurityAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "permissions:" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="CI_NO_PERMISSIONS", message="Workflow must declare minimal permissions block."))
        if "cancel-in-progress:" not in result.content:
            score -= 20
            blockers.append(Blocker(rule_id="CI_NO_CONCURRENCY", message="Workflow should cancel redundant in-progress runs."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"permissions": 50, "concurrency": 50},
            blockers=blockers,
            audit_summary="CI/CD pipeline approved." if score >= 85 else "Missing security permissions or concurrency."
        )


# ============================================================================
# 3. FinOps Token Optimizer
# ============================================================================
class PromptCompressor(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# LLM FinOps & Token Optimization Strategy

## 1. Prompt Caching Architecture (90% Cost Reduction)
- **Static Prefix Invariant:** Place immutable system prompts, schemas, and persona instructions at the absolute start of the prompt prefix.
- **Cache Break Prevention:** Never inject dynamic timestamps or request UUIDs into the top 1,024 cached tokens.
- **Savings Impact:** Repeated prompt prefix reads cost 10% of base input token pricing.

## 2. Dynamic Token Reduction & Context Pruning
- Strip redundant whitespace, markdown codeblock decorations, and comments in raw tool outputs.
- Minify JSON payloads before LLM ingestion.
- Implement AST-based code slicing to send only targeted functions instead of entire 2,000-line files.

## 3. Tiered Model Routing Table
| Task Complexity | Primary Model | Fallback Model | Target Cost / 1k Ops |
| :--- | :--- | :--- | :--- |
| **Classification / Routing** | Fast Flash (e.g. Claude Haiku / Flash) | - | < $0.001 |
| **Code Scaffolding** | Mid-Tier (Claude Sonnet / GPT-4o) | Fast Flash | < $0.015 |
| **Deep Reasoning & Architecture** | Reasoning Model (Opus / Pro / R1) | Mid-Tier | < $0.050 |
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class TokenCacheAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "Prompt Caching" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="FINOPS_NO_CACHING", message="Strategy must document prompt prefix caching."))
        if "Token Reduction" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="FINOPS_NO_PRUNING", message="Must document context pruning techniques."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"caching": 50, "routing": 50},
            blockers=blockers,
            audit_summary="FinOps token strategy approved." if score >= 85 else "Missing prompt caching or pruning."
        )


# ============================================================================
# Register All Phase 6 Skills
# ============================================================================
AgentRegistry.register("devops-docker-deploy", ContainerizationEngineer, DockerSecurityAuditor)
AgentRegistry.register("ci-cd-pipeline-builder", ActionsArchitect, PipelineSecurityAuditor)
AgentRegistry.register("finops-token-optimizer", PromptCompressor, TokenCacheAuditor)
