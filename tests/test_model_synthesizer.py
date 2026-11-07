"""Tests for NeuroSymbolicSynthesizer and BaseGenerator integration.

Verifies:
- Synthesizer initialization and auto-indexing of workspace skills.
- Context synthesis querying semantic VectorMemory.
- Text enrichment via statistical MarkovLanguageModel.
- Surgical blocker repair (SQL indexes, cascade rules, SLAs, Docker non-root user, RFC 7807, down migration).
- Integration with BaseGenerator and refine lifecycle.
- Latency benchmarks: synthesis and repair cycles complete in < 15ms.
"""

from __future__ import annotations

import time
import unittest
from pathlib import Path

from engine.core.base import BaseGenerator
from engine.core.types import Blocker, GenerationResult, Severity, TaskContext
from engine.model import MarkovLanguageModel, MemoryMatch, VectorMemory
from engine.model.synthesizer import NeuroSymbolicSynthesizer


class DummyGenerator(BaseGenerator):
    """Minimal generator for testing synthesizer integration."""

    def generate(self, context: TaskContext) -> GenerationResult:
        return GenerationResult(
            skill_name=self.skill_name,
            content=f"Initial content for {context.prompt}",
            metadata={"source": "dummy"},
        )


class TestModelSynthesizer(unittest.TestCase):
    """TDD unit tests for NeuroSymbolicSynthesizer and BaseGenerator integration."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialize a pre-warmed synthesizer instance for tests."""
        cls.synthesizer = NeuroSymbolicSynthesizer(auto_index_skills=True)

    def test_synthesizer_initialization(self) -> None:
        """Verify synthesizer initializes, auto-indexes skills, and respects flags."""
        synth = self.synthesizer
        self.assertIsNotNone(synth.memory)
        self.assertIsNotNone(synth.lm)

        # Auto-indexed skills verification
        skills_dir = Path("skills")
        if skills_dir.exists():
            self.assertGreaterEqual(synth.memory.document_count, 30)
            self.assertGreater(synth.lm.vocab_size, 500)
            self.assertGreater(len(synth.lm.transitions), 500)

        # Initialization with auto_index_skills=False
        synth_empty = NeuroSymbolicSynthesizer(auto_index_skills=False)
        self.assertEqual(synth_empty.memory.document_count, 0)
        self.assertEqual(len(synth_empty.lm.transitions), 0)

        # Initialization with custom memory and LM
        custom_vm = VectorMemory()
        custom_lm = MarkovLanguageModel()
        synth_custom = NeuroSymbolicSynthesizer(
            memory=custom_vm,
            lm=custom_lm,
            auto_index_skills=False,
        )
        self.assertIs(synth_custom.memory, custom_vm)
        self.assertIs(synth_custom.lm, custom_lm)

    def test_context_synthesis(self) -> None:
        """Verify context synthesis returns relevant skill snippets for semantic queries."""
        skills_dir = Path("skills")
        if not skills_dir.exists():
            self.skipTest("skills directory not found")

        matches = self.synthesizer.synthesize_context(
            prompt="database migrations zero downtime indexes",
            domain="database",
            top_k=3,
        )
        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)
        self.assertLessEqual(len(matches), 3)

        # All matches should be MemoryMatch instances sorted by score descending
        for match in matches:
            self.assertIsInstance(match, MemoryMatch)
            self.assertGreater(match.score, 0.0)

        top_hit = matches[0].doc_id
        self.assertTrue(
            "backend-schema" in top_hit or "db-migration-optimizer" in top_hit,
            f"Expected database skill as top hit, got {top_hit}",
        )

        # DevOps query
        devops_matches = self.synthesizer.synthesize_context(
            prompt="Docker container multi-stage build non-root",
            domain="devops",
            top_k=3,
        )
        self.assertGreater(len(devops_matches), 0)
        self.assertIn("devops-docker-deploy", devops_matches[0].doc_id)

        # Empty query handling
        self.assertEqual(self.synthesizer.synthesize_context(""), [])

    def test_enrich_text(self) -> None:
        """Verify text enrichment produces continuations using MarkovLanguageModel."""
        seed = "The system architecture"
        enriched = self.synthesizer.enrich_text(
            seed_text=seed,
            domain="distributed systems",
            max_new_tokens=25,
            temperature=0.7,
        )
        self.assertIsInstance(enriched, str)
        self.assertTrue(enriched.startswith(seed))
        self.assertGreaterEqual(len(enriched), len(seed))

        # Empty seed text handling with domain
        empty_enriched = self.synthesizer.enrich_text(
            seed_text="",
            domain="database schema",
            max_new_tokens=10,
        )
        self.assertIsInstance(empty_enriched, str)

    def test_repair_blockers(self) -> None:
        """Verify surgical blocker repair for all critical architectural rules."""
        # 1. SQL Indexes repair
        sql_content = "CREATE TABLE users (id UUID PRIMARY KEY, email VARCHAR(255) NOT NULL);"
        repaired_sql = self.synthesizer.repair(sql_content, ["missing composite index"])
        self.assertIn("CREATE INDEX", repaired_sql)
        self.assertIn("IF NOT EXISTS", repaired_sql)

        # 2. Foreign Key ON DELETE CASCADE repair
        fk_content = "user_id UUID NOT NULL REFERENCES users(id),"
        repaired_fk = self.synthesizer.repair(fk_content, ["missing ON DELETE CASCADE"])
        self.assertIn("REFERENCES users(id) ON DELETE CASCADE", repaired_fk)

        # 3. SLA and Latency budgets repair
        doc_content = "# Technical Architecture\nSpecification details."
        repaired_sla = self.synthesizer.repair(
            doc_content,
            ["missing SLA and p95 latency budget", "p99 target undefined"],
        )
        self.assertIn("p95", repaired_sla)
        self.assertIn("p99", repaired_sla)
        self.assertTrue("SLA" in repaired_sla or "99." in repaired_sla)

        # 4. Docker non-root user repair
        docker_content = (
            "FROM python:3.11-slim\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "CMD [\"python\", \"main.py\"]\n"
        )
        repaired_docker = self.synthesizer.repair(docker_content, ["missing non-root user (USER)"])
        self.assertIn("USER appuser", repaired_docker)
        self.assertLess(repaired_docker.index("USER appuser"), repaired_docker.index("CMD"))

        # 5. RFC 7807 error schema repair
        api_content = "openapi: 3.1.0\ninfo:\n  title: API\npaths: {}\n"
        repaired_api = self.synthesizer.repair(api_content, ["missing RFC 7807 error envelope"])
        self.assertIn("RFC 7807", repaired_api)
        self.assertIn("application/problem+json", repaired_api)

        # 6. Down migration / rollback repair
        migration_content = "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;"
        repaired_down = self.synthesizer.repair(migration_content, ["missing rollback down migration"])
        self.assertTrue(
            "down migration" in repaired_down.lower() or "rollback" in repaired_down.lower()
        )

        # 7. Multiple simultaneous blockers repair
        multi_content = (
            "CREATE TABLE orders (\n"
            "    id UUID PRIMARY KEY,\n"
            "    user_id UUID REFERENCES users(id)\n"
            ");"
        )
        repaired_multi = self.synthesizer.repair(
            multi_content,
            ["no index defined", "cascade deletion missing"],
        )
        self.assertIn("CREATE INDEX", repaired_multi)
        self.assertIn("ON DELETE CASCADE", repaired_multi)

        # 8. Handling Blocker dataclass objects
        blocker_obj = Blocker(
            rule_id="DB_NO_INDEX",
            message="Backend schema must define composite or foreign key indexes.",
            severity=Severity.BLOCKER,
        )
        repaired_from_obj = self.synthesizer.repair(sql_content, [blocker_obj])
        self.assertIn("CREATE INDEX", repaired_from_obj)

        # 9. Markdown code fence insertion positioning
        md_sql = "# Database Schema\n\n```sql\nCREATE TABLE items (id INT);\n```\n"
        repaired_md = self.synthesizer.repair(md_sql, ["no index defined"])
        self.assertIn("CREATE INDEX", repaired_md)
        sql_block = repaired_md[repaired_md.find("```sql") : repaired_md.rfind("```")]
        self.assertIn("CREATE INDEX", sql_block)

        # 10. Additional rules: lock timeout and Docker healthcheck
        md_migration = "# Migration\n\n```sql\nALTER TABLE users ADD COLUMN name TEXT;\n```\n"
        repaired_timeout = self.synthesizer.repair(md_migration, ["lock_timeout missing"])
        self.assertIn("SET lock_timeout = '2s';", repaired_timeout)

        docker_hc = "FROM alpine\nCMD [\"sh\"]\n"
        repaired_hc = self.synthesizer.repair(docker_hc, ["docker_no_healthcheck"])
        self.assertIn("HEALTHCHECK", repaired_hc)

    def test_base_generator_integration(self) -> None:
        """Verify BaseGenerator accepts synthesizer, delegates context retrieval and refinement."""
        gen = DummyGenerator(
            name="test_generator",
            skill_name="backend-schema",
            role="Generator",
            synthesizer=self.synthesizer,
        )

        # synthesize_context delegation
        context_items = gen.synthesize_context("PostgreSQL database migrations", domain="database")
        self.assertIsInstance(context_items, list)
        self.assertGreater(len(context_items), 0)

        # Generator without synthesizer fallback
        gen_plain = DummyGenerator(
            name="plain_generator",
            skill_name="test-skill",
            role="Generator",
        )
        self.assertIsNone(gen_plain.synthesizer)
        self.assertEqual(gen_plain.synthesize_context("anything"), [])

        # Refinement loop with synthesizer
        context = TaskContext(skill_name="backend-schema", prompt="Create users table")
        prev_result = GenerationResult(
            skill_name="backend-schema",
            content="CREATE TABLE users (id UUID PRIMARY KEY, team_id UUID REFERENCES teams(id));",
        )
        blockers = [
            Blocker(rule_id="DB_NO_INDEX", message="missing composite index"),
            Blocker(rule_id="DB_NO_CASCADE", message="missing ON DELETE CASCADE"),
        ]
        refined_result = gen.refine(context, prev_result, blockers)
        self.assertIsInstance(refined_result, GenerationResult)
        self.assertIn("CREATE INDEX", refined_result.content)
        self.assertIn("ON DELETE CASCADE", refined_result.content)

    def test_latency_benchmark(self) -> None:
        """Verify synthesis and repair cycles complete in < 15ms on standard hardware."""
        synth = self.synthesizer
        content = (
            "CREATE TABLE orders (\n"
            "    id UUID PRIMARY KEY,\n"
            "    user_id UUID REFERENCES users(id)\n"
            ");"
        )
        blockers = ["missing composite index", "missing ON DELETE CASCADE", "missing SLA"]

        # Run 10 consecutive synthesis + repair cycles
        iterations = 10
        start = time.perf_counter()
        for _ in range(iterations):
            _ = synth.synthesize_context("database schema indexes", domain="database", top_k=3)
            _ = synth.repair(content, blockers)
        total_time_ms = (time.perf_counter() - start) * 1000.0
        avg_cycle_ms = total_time_ms / iterations

        self.assertLess(
            avg_cycle_ms,
            15.0,
            f"Average cycle latency {avg_cycle_ms:.2f}ms exceeds 15ms target",
        )


if __name__ == "__main__":
    unittest.main()
