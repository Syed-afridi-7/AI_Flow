import unittest
import time
import engine.agents
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
from engine.core.types import TaskContext


SAMPLE_PROMPTS = {
    # Phase 1: Architecture
    "prd-generator": "Multi-tenant CRM platform for real estate brokers",
    "trd-generator": "High-throughput telemetry ingestion pipeline",
    "app-flow": "Onboarding wizard and workspace setup state transitions",
    "uiux-design-brief": "Fintech trading dashboard with dark mode and emerald accents",
    "backend_schema": "E-commerce platform with Users, Products, Orders, OrderItems",
    "backend-schema": "E-commerce platform with Users, Products, Orders, OrderItems",
    "system-architecture": "Distributed real-time notification engine with Redis and WebSocket",
    "implementation-plan": "Refactor authentication layer from session cookies to JWT",
    
    # Phase 2: Execution
    "task-to-skill": "Automated database migration rollback verification workflow",
    "playwright-e2e-testing": "User login, project creation, and settings persistence",
    "systematic-debugging": "Intermittent HTTP 504 gateway timeout under concurrent load",

    # Phase 3: Release
    "security-gap-audit": "Pre-launch security audit of payment checkout webhook",
    "dead-code-cleanup": "Audit unused legacy auth functions and orphaned helpers",
    "rigorous-code-review": "Review pull request adding rate-limiting middleware",
    "clean-git-commits": "feat(api): implement idempotent webhook delivery verification",

    # Phase 4: Design & Frontend
    "design-system-tokens": "Accessible multi-brand theme tokens with dark mode parity",
    "landing-page-converter": "B2B SaaS API monitoring platform for engineering teams",
    "accessibility-wcag-audit": "Audit keyboard navigation and focus management on modals",

    # Phase 5: API, Data & Performance
    "api-contract-generator": "User profile management and billing subscription endpoints",
    "db-migration-optimizer": "Add email_verified column and concurrent composite index",
    "performance-profiling": "Optimize slow LCP on landing page and resolve memory leak",

    # Phase 6: DevOps, CI/CD & FinOps
    "devops-docker-deploy": "Hardened multi-stage Dockerfile for FastAPI microservice",
    "ci-cd-pipeline-builder": "GitHub Actions workflow for automated testing and release",
    "finops-token-optimizer": "Static prefix caching and context pruning for LLM calls",

    # Phase 7: Freelance Operations
    "freelance-client-onboarding": "Full-stack mobile app MVP development proposal and SOW",
    "email-inbox-triage": "Urgent client request for staging demo bug fix before investor meeting",
    "invoice-billing-tracker": "Milestone 2 deliverable invoice for $4,500 due in 15 days",

    # Phase 8: Social Growth & Founder OS
    "insta-reel-creator": "Why you do not need cloud API keys to build autonomous AI agents",
    "seo-content-strategist": "Topic cluster for pure Python agent frameworks without cloud API",
    "social-copy-repurposer": "Turn engineering devlog on AST static analysis into Twitter thread",
    "executive-time-ledger": "Weekly calendar audit for technical founder allocating deep work",
}


class TestAll60Agents(unittest.TestCase):
    def setUp(self):
        self.runner = DualAgentRunner()

    def test_all_30_skills_count(self):
        skills = AgentRegistry.list_skills()
        self.assertEqual(len(skills), 30, f"Expected exactly 30 skills, got {len(skills)}: {skills}")

    def test_execute_all_30_skills_dual_mode(self):
        skills = AgentRegistry.list_skills()
        start_time = time.time()
        passed_count = 0

        for skill in skills:
            with self.subTest(skill=skill):
                prompt = SAMPLE_PROMPTS.get(skill, f"Standard execution prompt for {skill}")
                result, scorecard = self.runner.run_skill(
                    skill_name=skill,
                    prompt=prompt,
                    mode="dual"
                )
                self.assertIsNotNone(result.content, f"{skill} returned None content")
                self.assertGreater(len(result.content), 50, f"{skill} output too short ({len(result.content)} bytes)")
                self.assertTrue(scorecard.passed, f"{skill} failed validation with score {scorecard.score}: {scorecard.blockers}")
                self.assertGreaterEqual(scorecard.score, 85, f"{skill} score {scorecard.score} below 85")
                passed_count += 1

        elapsed = time.time() - start_time
        print(f"\n⚡ Executed all {len(skills)} skills (60 agents) in {elapsed:.3f}s. All passed!")
        self.assertEqual(passed_count, 30)
        self.assertLess(elapsed, 5.0, "All 60 agents must execute in under 5.0 seconds")


if __name__ == "__main__":
    unittest.main()
