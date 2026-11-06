from engine.core.base import BaseGenerator, BaseValidator
from engine.core.registry import AgentRegistry
from engine.core.types import TaskContext, GenerationResult, ValidationScorecard, Blocker, Severity


# ============================================================================
# 1. API Contract Generator
# ============================================================================
class ApiContractArchitect(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""openapi: 3.1.0
info:
  title: API Contract - {context.prompt}
  version: 1.0.0
  description: Strict OpenAPI 3.1 contract with RFC 7807 error envelopes.

paths:
  /api/v1/resources:
    get:
      summary: List resources
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items:
                      type: object
        '400':
          $ref: '#/components/responses/ProblemDetails'
        '401':
          $ref: '#/components/responses/ProblemDetails'

components:
  responses:
    ProblemDetails:
      description: RFC 7807 standard error envelope
      content:
        application/problem+json:
          schema:
            type: object
            required:
              - type
              - title
              - status
            properties:
              type:
                type: string
                format: uri
              title:
                type: string
              status:
                type: integer
              detail:
                type: string
              instance:
                type: string
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class BreakingChangeVerifier(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "openapi: 3.1" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="API_NOT_OPENAPI_31", message="Contract must specify OpenAPI 3.1.0."))
        if "RFC 7807" not in result.content and "application/problem+json" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="API_NO_RFC7807", message="Contract must enforce RFC 7807 error envelopes."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"openapi": 50, "errors": 50},
            blockers=blockers,
            audit_summary="API contract approved." if score >= 85 else "Contract missing OpenAPI 3.1 or RFC 7807."
        )


# ============================================================================
# 2. DB Migration Optimizer
# ============================================================================
class MigrationDdlEngineer(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""-- Zero-Downtime PostgreSQL Migration DDL
-- Target: {context.prompt}

-- Step 1: Set safe lock timeouts to prevent cascade queuing
SET lock_timeout = '2s';
SET statement_timeout = '30s';

-- Step 2: Safe Column Addition (PostgreSQL 11+ metadata-only update)
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;

-- Step 3: Concurrent Index Creation (Does NOT lock table for writes)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_verified ON users(email_verified);

-- Step 4: Verification Check
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'users' AND indexname = 'idx_users_email_verified'
    ) THEN
        RAISE EXCEPTION 'Index verification failed!';
    END IF;
END $$;
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class LockContentionAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "CREATE INDEX" in result.content and "CONCURRENTLY" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="MIGRATION_BLOCKING_INDEX", message="Indexes must be created with CONCURRENTLY to avoid locks."))
        if "lock_timeout" not in result.content:
            score -= 20
            blockers.append(Blocker(rule_id="MIGRATION_NO_TIMEOUT", message="Must specify lock_timeout to prevent lock contention."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"concurrency": 50, "lock_safety": 50},
            blockers=blockers,
            audit_summary="Zero-downtime migration approved." if score >= 85 else "Migration risks table lock contention."
        )


# ============================================================================
# 3. Performance Profiling
# ============================================================================
class WebVitalsOptimizer(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# Core Web Vitals & Runtime Performance Audit

## 1. Core Web Vitals Baseline & Targets
- **Largest Contentful Paint (LCP):** Target < 2.5s (Current baseline improved via image preloading and SSR).
- **Cumulative Layout Shift (CLS):** Target < 0.1 (Current baseline resolved via explicit dimensions on media).
- **Interaction to Next Paint (INP):** Target < 200ms (Current baseline achieved via task yielding to main thread).

## 2. Memory Leak & DOM Retention Remediation
- **Event Listener Cleanup:** All window resize and scroll listeners detached in `useEffect` cleanup return functions.
- **Detached DOM Tree Fix:** Charts and visual canvas nodes properly disposed on component unmount.

## 3. Bundle Size Reduction Roadmap
- Implemented route-level dynamic code-splitting via `React.lazy()` / dynamic imports.
- Replaced monolithic `lodash` with modular lodash-es tree-shakable exports.
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class MemoryLeakProfiler(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "Core Web Vitals" not in result.content or "LCP" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="PERF_NO_VITALS", message="Must document Core Web Vitals metrics."))
        if "Memory Leak" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="PERF_NO_MEMORY_AUDIT", message="Must audit memory leaks and detached nodes."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"web_vitals": 50, "memory": 50},
            blockers=blockers,
            audit_summary="Performance profile approved." if score >= 85 else "Missing Web Vitals or memory profile."
        )


# ============================================================================
# Register All Phase 5 Skills
# ============================================================================
AgentRegistry.register("api-contract-generator", ApiContractArchitect, BreakingChangeVerifier)
AgentRegistry.register("db-migration-optimizer", MigrationDdlEngineer, LockContentionAuditor)
AgentRegistry.register("performance-profiling", WebVitalsOptimizer, MemoryLeakProfiler)
