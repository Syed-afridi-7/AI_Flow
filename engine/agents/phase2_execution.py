from engine.core.base import BaseGenerator, BaseValidator
from engine.core.registry import AgentRegistry
from engine.core.types import TaskContext, GenerationResult, ValidationScorecard, Blocker, Severity


# ============================================================================
# 1. Task to Skill
# ============================================================================
class WorkflowExtractor(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        topic = context.prompt.strip() or "engineering-workflow"
        skill_id = topic.lower().replace(" ", "-")[:30]
        content = f"""---
name: {skill_id}
description: "Standardized workflow for {topic} with deterministic execution gates."
---

# {topic.title()} Skill

## 1. Triggering Conditions
- Use when preparing or executing: {topic}.
- Target artifact file: `SKILL.md`.
- Trigger on commands matching '{skill_id}'.

## 2. Step-by-Step Workflow
1. **Pre-Flight Audit:** Inspect current repository state and prerequisites.
2. **Execution:** Execute changes atomically with strict error checking.
3. **Verification:** Run test suite and check outputs against acceptance criteria.
4. **Documentation:** Record changes and update tracking files.

## 3. Failure Modes & Recovery
- **Failure:** Test assertion fails or command exits non-zero.
- **Recovery:** Revert working changes and inspect error logs before retry.
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class SpecComplianceVerifier(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "---" not in result.content or "description:" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="SKILL_NO_FRONTMATTER", message="Skill must contain YAML frontmatter with description."))
        if "Triggering Conditions" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="SKILL_NO_TRIGGERS", message="Skill must define triggering conditions."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"frontmatter": 50, "workflow": 50},
            blockers=blockers,
            audit_summary="Skill spec approved." if score >= 85 else "Skill missing frontmatter or triggers."
        )


# ============================================================================
# 2. Playwright E2E Testing
# ============================================================================
class BrowserAutomationEngineer(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""import {{ test, expect }} from '@playwright/test';

test.describe('End-to-End User Journeys: {context.prompt}', () => {{
    test.use({{ storageState: 'playwright/.auth/user.json' }});

    test('should authenticate and execute core flow successfully', async ({{ page }}) => {{
        await page.goto('/dashboard');
        await expect(page.getByRole('heading', {{ level: 1 }})).toBeVisible();

        const actionButton = page.getByRole('button', {{ name: /create|submit|launch/i }});
        await expect(actionButton).toBeEnabled();
        await actionButton.click();

        await expect(page.getByRole('alert')).toContainText(/success|created/i);
    }});

    test('should handle network timeout gracefully', async ({{ page }}) => {{
        await page.route('**/api/v1/**', route => route.abort());
        await page.goto('/dashboard');
        await expect(page.getByText(/unable to load|retry/i)).toBeVisible();
    }});
}});
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class FlakinessDeterminismAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "waitForTimeout" in result.content:
            score -= 50
            blockers.append(Blocker(rule_id="E2E_HARDCODED_SLEEP", message="Hardcoded waitForTimeout sleeps cause flakiness."))
        if "getByRole" not in result.content and "getByText" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="E2E_NO_ACCESSIBLE_LOCATOR", message="Tests should prefer accessible role/text locators."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"determinism": 50, "locators": 50},
            blockers=blockers,
            audit_summary="Playwright tests approved." if score >= 85 else "Playwright tests have anti-patterns."
        )


# ============================================================================
# 3. Systematic Debugging
# ============================================================================
class RootCauseInvestigator(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# Systematic Debugging Protocol

## 1. Symptom Restatement & Boundary
**Observed Bug:** {context.prompt}
**Expected Behavior:** System functions deterministically without premature failure.

## 2. Three Competing Hypotheses
- **Hypothesis 1 (TTL / Expiration Misconfiguration):** Session expiration timer or token TTL is set in seconds instead of milliseconds.
- **Hypothesis 2 (Middleware Cache Race):** Concurrency race in redis session cache refreshes eviction timestamp prematurely.
- **Hypothesis 3 (Clock Skew / NTP Desync):** Client and server timestamp calculation differences trigger early invalidation.

## 3. Disproof Probes & Diagnostic Commands
```bash
# Probe 1: Verify token payload and exp timestamp
python -c "import jwt; print(jwt.decode(token, options={{'verify_signature': False}}))"
# Probe 2: Monitor Redis key TTL
redis-cli ttl "session:test_user_id"
```

## 4. Root Cause Isolation & Minimal Verified Fix
- **Root Cause Confirmed:** Hypothesis 1 verified. Expiration threshold was evaluated with unit mismatch.
- **Minimal Fix:** Update configuration parser to strictly cast duration using integer seconds.
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class RegressionProofVerifier(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "Hypothesis 1" not in result.content or "Hypothesis 2" not in result.content or "Hypothesis 3" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="DEBUG_NOT_3_HYPOTHESES", message="Debugging protocol mandates at least 3 distinct hypotheses."))
        if "Root Cause" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="DEBUG_NO_ROOT_CAUSE", message="Must document isolated root cause."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"hypotheses": 50, "proof": 50},
            blockers=blockers,
            audit_summary="Debugging protocol passed." if score >= 85 else "Debugging protocol incomplete."
        )


# ============================================================================
# Register All Phase 2 Skills
# ============================================================================
AgentRegistry.register("task-to-skill", WorkflowExtractor, SpecComplianceVerifier)
AgentRegistry.register("playwright-e2e-testing", BrowserAutomationEngineer, FlakinessDeterminismAuditor)
AgentRegistry.register("systematic-debugging", RootCauseInvestigator, RegressionProofVerifier)
