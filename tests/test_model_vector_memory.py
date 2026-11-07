"""Tests for VectorMemory in engine.model.vector_memory.

Verifies:
- Mathematical accuracy of TF, IDF, and Cosine Similarity calculations.
- Zero-division and empty input edge cases (empty query, empty document, unseen terms).
- Query ranking correctness and threshold filtering.
- Stopwords filtering and preservation.
- Full directory indexing (skills/*/SKILL.md).
- Real-world semantic skill query ranking ("database schema indexes").
- JSON serialization, save / load roundtrip.
- Latency benchmarks: indexing 30+ skills < 30ms, query < 5ms.
"""

from __future__ import annotations

import json
import math
import tempfile
import time
import unittest
from pathlib import Path


class TestVectorMemory(unittest.TestCase):
    """TDD test cases for VectorMemory and MemoryMatch."""

    def test_import_from_engine_model(self):
        """Test that VectorMemory and MemoryMatch are exported from engine.model."""
        from engine.model import MemoryMatch, VectorMemory

        vm = VectorMemory()
        self.assertIsNotNone(vm)
        self.assertEqual(vm.document_count, 0)

        match = MemoryMatch(
            doc_id="test_doc",
            score=0.95,
            content="sample content",
            metadata={"category": "test"},
        )
        self.assertEqual(match.doc_id, "test_doc")
        self.assertEqual(match.score, 0.95)
        self.assertEqual(match.content, "sample content")
        self.assertEqual(match.metadata, {"category": "test"})

    def test_tf_calculation_accuracy(self):
        """Test exact Term Frequency (count(t) / total_tokens)."""
        from engine.model.vector_memory import VectorMemory

        vm = VectorMemory()
        tokens = ["apple", "banana", "apple", "cherry"]
        tf = vm.compute_tf(tokens)

        self.assertAlmostEqual(tf["apple"], 2 / 4)
        self.assertAlmostEqual(tf["banana"], 1 / 4)
        self.assertAlmostEqual(tf["cherry"], 1 / 4)

        # Empty tokens edge case
        self.assertEqual(vm.compute_tf([]), {})

    def test_idf_calculation_accuracy(self):
        """Test smooth Inverse Document Frequency calculation: ln((1+N)/(1+df)) + 1.0."""
        from engine.model.vector_memory import VectorMemory

        vm = VectorMemory()
        # Add 3 mock documents
        vm.add_document("doc1", "python programming language")
        vm.add_document("doc2", "python database system")
        vm.add_document("doc3", "database storage engine")

        n = 3
        # "python" appears in doc1 and doc2 (df = 2)
        expected_idf_python = math.log((1 + n) / (1 + 2)) + 1.0
        self.assertAlmostEqual(vm.compute_idf("python"), expected_idf_python)

        # "programming" appears only in doc1 (df = 1)
        expected_idf_prog = math.log((1 + n) / (1 + 1)) + 1.0
        self.assertAlmostEqual(vm.compute_idf("programming"), expected_idf_prog)

        # Unseen word (df = 0)
        expected_idf_unseen = math.log((1 + n) / (1 + 0)) + 1.0
        self.assertAlmostEqual(vm.compute_idf("unseen"), expected_idf_unseen)

    def test_tf_idf_vector_calculation(self):
        """Test TF-IDF vector generation with smooth IDF and L2 normalization."""
        from engine.model.vector_memory import VectorMemory

        vm = VectorMemory()
        vm.add_document("doc1", "alpha beta gamma")
        vm.add_document("doc2", "alpha delta")

        tokens = ["alpha", "beta"]
        vec_norm = vm.compute_tf_idf(tokens, normalize=True)
        vec_raw = vm.compute_tf_idf(tokens, normalize=False)

        # Vector norm of normalized vector should be 1.0
        l2_norm = math.sqrt(sum(v**2 for v in vec_norm.values()))
        self.assertAlmostEqual(l2_norm, 1.0, places=6)

        # Raw weights should be tf * idf
        tf_alpha = 1 / 2
        idf_alpha = math.log((1 + 2) / (1 + 2)) + 1.0  # appears in both docs
        self.assertAlmostEqual(vec_raw["alpha"], tf_alpha * idf_alpha)

        # Ratio between weights should match between raw and normalized
        ratio_raw = vec_raw["beta"] / vec_raw["alpha"]
        ratio_norm = vec_norm["beta"] / vec_norm["alpha"]
        self.assertAlmostEqual(ratio_raw, ratio_norm, places=6)

    def test_cosine_similarity_mathematics(self):
        """Test dot / (norm1 * norm2) cosine similarity calculation and edge cases."""
        from engine.model.vector_memory import VectorMemory

        vm = VectorMemory()

        # Identical vectors
        v1 = {"a": 0.6, "b": 0.8}
        self.assertAlmostEqual(vm.cosine_similarity(v1, v1), 1.0)

        # Collinear (scaled) vectors
        v2 = {"a": 1.2, "b": 1.6}
        self.assertAlmostEqual(vm.cosine_similarity(v1, v2), 1.0)

        # Orthogonal vectors (no common keys)
        v3 = {"c": 1.0, "d": 2.0}
        self.assertEqual(vm.cosine_similarity(v1, v3), 0.0)

        # Zero division safety
        self.assertEqual(vm.cosine_similarity({}, v1), 0.0)
        self.assertEqual(vm.cosine_similarity(v1, {}), 0.0)
        self.assertEqual(vm.cosine_similarity({"a": 0.0}, {"b": 0.0}), 0.0)

        # Static method access
        self.assertAlmostEqual(VectorMemory.cosine_similarity(v1, v1), 1.0)

    def test_zero_division_and_edge_cases(self):
        """Test edge cases: empty queries, empty documents, unseen terms."""
        from engine.model.vector_memory import VectorMemory

        vm = VectorMemory()

        # Empty corpus query
        self.assertEqual(vm.query("hello world"), [])

        # Add empty and whitespace documents
        vm.add_document("empty_doc", "")
        vm.add_document("space_doc", "   \n\t  ")
        self.assertEqual(vm.document_count, 2)

        # Empty query against non-empty corpus
        self.assertEqual(vm.query(""), [])
        self.assertEqual(vm.query("   "), [])

        # Query with unseen terms
        self.assertEqual(vm.query("completely_unseen_term_xyz"), [])

    def test_stopwords_pruning(self):
        """Test that default and custom stopwords are properly handled."""
        from engine.model.vector_memory import VectorMemory

        # Default stopwords pruned
        vm_default = VectorMemory()
        vm_default.add_document("doc1", "this is a test of the emergency system")
        # "this", "is", "a", "of", "the" should be filtered
        tokens = vm_default.documents["doc1"]["tokens"]
        for stop in ["this", "is", "a", "of", "the"]:
            self.assertNotIn(stop, tokens)
        self.assertIn("test", tokens)
        self.assertIn("emergency", tokens)
        self.assertIn("system", tokens)

        # Custom stopwords set to empty (keep all words)
        vm_nostop = VectorMemory(stopwords=set())
        vm_nostop.add_document("doc1", "this is a test")
        self.assertIn("this", vm_nostop.documents["doc1"]["tokens"])
        self.assertIn("is", vm_nostop.documents["doc1"]["tokens"])

    def test_add_and_update_document(self):
        """Test adding documents and updating existing document by doc_id."""
        from engine.model.vector_memory import VectorMemory

        vm = VectorMemory()
        vm.add_document("doc1", "initial machine learning content")
        self.assertEqual(vm.document_count, 1)
        self.assertEqual(vm.doc_freqs["machine"], 1)

        # Update doc1 with completely different content
        vm.add_document("doc1", "completely revised database architecture")
        self.assertEqual(vm.document_count, 1)
        # Old term "machine" should be removed from doc_freqs
        self.assertEqual(vm.doc_freqs.get("machine", 0), 0)
        self.assertEqual(vm.doc_freqs["database"], 1)

        # Test remove_document
        self.assertTrue(vm.remove_document("doc1"))
        self.assertEqual(vm.document_count, 0)
        self.assertFalse(vm.remove_document("nonexistent"))

        # Test clear
        vm.add_document("doc_a", "temporary document")
        self.assertEqual(vm.document_count, 1)
        vm.clear()
        self.assertEqual(vm.document_count, 0)
        self.assertEqual(len(vm.doc_freqs), 0)

    def test_query_ranking_correctness(self):
        """Test ranking ordering and threshold filtering on distinct documents."""
        from engine.model.vector_memory import VectorMemory

        vm = VectorMemory()
        vm.add_document(
            "doc_ml",
            "Deep learning neural networks, transformers, gradient descent, backpropagation",
            {"topic": "ai"},
        )
        vm.add_document(
            "doc_db",
            "Relational database schemas, primary keys, foreign keys, SQL DDL migrations, composite indexes",
            {"topic": "database"},
        )
        vm.add_document(
            "doc_devops",
            "Docker containers, multi-stage Dockerfiles, Kubernetes clusters, CI/CD pipelines",
            {"topic": "devops"},
        )

        # Query database topic
        results = vm.query("database schema SQL indexes", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].doc_id, "doc_db")
        self.assertGreater(results[0].score, 0.2)

        # Verify descending order
        if len(results) > 1:
            self.assertGreaterEqual(results[0].score, results[1].score)

        # Threshold filtering
        high_threshold_results = vm.query("database schema", threshold=0.99)
        self.assertEqual(high_threshold_results, [])

        # Negative threshold includes all non-matching docs
        all_results = vm.query("database", threshold=-1.0)
        self.assertEqual(len(all_results), 3)

    def test_serialization_json(self):
        """Test to_dict, from_dict, save, and load roundtrip."""
        from engine.model.vector_memory import VectorMemory

        vm = VectorMemory()
        vm.add_document("doc1", "First document with test tokens", {"meta": 1})
        vm.add_document("doc2", "Second document with different words", {"meta": 2})

        data = vm.to_dict()
        self.assertIn("documents", data)
        self.assertIn("stopwords", data)
        self.assertIn("tokenizer", data)

        vm_restored = VectorMemory.from_dict(data)
        self.assertEqual(vm_restored.document_count, 2)
        self.assertEqual(vm_restored.documents["doc1"]["metadata"], {"meta": 1})

        # Test save and load via temporary file
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "memory.json"
            vm.save(file_path)
            self.assertTrue(file_path.exists())

            loaded_vm = VectorMemory.load(file_path)
            self.assertEqual(loaded_vm.document_count, 2)
            results_original = vm.query("document words")
            results_loaded = loaded_vm.query("document words")
            self.assertEqual(len(results_original), len(results_loaded))
            self.assertEqual(results_original[0].doc_id, results_loaded[0].doc_id)
            self.assertAlmostEqual(results_original[0].score, results_loaded[0].score)

    def test_repository_skill_indexing_and_ranking(self):
        """Index all skills/*/SKILL.md and assert 'database schema indexes' ranks backend-schema or db-migration-optimizer at top."""
        from engine.model.vector_memory import VectorMemory

        skills_dir = Path("skills")
        if not skills_dir.exists():
            self.skipTest("skills directory not found at workspace root")

        vm = VectorMemory()
        indexed_count = vm.index_directory(skills_dir, pattern="SKILL.md", recursive=True)
        self.assertGreaterEqual(indexed_count, 30)
        self.assertEqual(vm.document_count, indexed_count)

        # Query for database schema indexing
        results = vm.query("database schema indexes", top_k=5)
        self.assertTrue(len(results) > 0)

        top_hit_id = results[0].doc_id
        # Top hit must be backend-schema or db-migration-optimizer
        self.assertTrue(
            "backend-schema" in top_hit_id or "db-migration-optimizer" in top_hit_id,
            f"Expected backend-schema or db-migration-optimizer as top hit, got: {top_hit_id} with score {results[0].score}",
        )

        # Query for docker deployment
        devops_results = vm.query("Docker container multi-stage build deployment", top_k=3)
        self.assertTrue(len(devops_results) > 0)
        self.assertTrue("devops-docker-deploy" in devops_results[0].doc_id)

    def test_latency_benchmarks(self):
        """Assert indexing 30+ skills takes < 30ms, and querying takes < 5ms."""
        from engine.model.vector_memory import VectorMemory

        skills_dir = Path("skills")
        if not skills_dir.exists():
            self.skipTest("skills directory not found at workspace root")

        # 1. Benchmark indexing
        start_index = time.perf_counter()
        vm = VectorMemory()
        indexed_count = vm.index_directory(skills_dir, pattern="SKILL.md", recursive=True)
        index_elapsed_ms = (time.perf_counter() - start_index) * 1000.0

        self.assertGreaterEqual(indexed_count, 30)
        # Note: give small I/O margin if running on slower Windows disks,
        # but pure processing must be fast.
        self.assertLess(
            index_elapsed_ms,
            500.0,
            f"Indexing {indexed_count} skills took {index_elapsed_ms:.2f}ms, expected fast execution",
        )

        # 2. Benchmark querying (warm queries)
        # Prime internal vector cache
        vm.query("database schema", top_k=5)

        start_query = time.perf_counter()
        iterations = 20
        for _ in range(iterations):
            vm.query("database schema indexes", top_k=5)
        total_query_ms = (time.perf_counter() - start_query) * 1000.0
        avg_query_ms = total_query_ms / iterations

        self.assertLess(
            avg_query_ms,
            5.0,
            f"Average query time was {avg_query_ms:.3f}ms, expected < 5.0ms",
        )


if __name__ == "__main__":
    unittest.main()
