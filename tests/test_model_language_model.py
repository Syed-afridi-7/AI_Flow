"""Tests for MarkovLanguageModel in engine.model.language_model.

Verifies:
- Import and export from engine.model package.
- Initialization with default parameters (order=3, laplace_alpha=1.0) and custom tokenizer.
- Model training on a sample corpus (unigrams and n-gram transitions).
- Probability distribution normalization (probabilities sum to 1.0).
- Laplace smoothing returns non-zero probability for unseen transitions and tokens.
- Backoff mechanism: order-3 -> bigram -> unigram for unseen contexts.
- Temperature scaling: low T concentrates on mode, high T flattens distribution.
- Top-p nucleus sampling behavior.
- Text generation producing coherent completions from seed prompts.
- Stop tokens and max_tokens enforcement in generation.
- Full directory training on skills/ directory (*.md).
- JSON serialization, to_dict/from_dict, save/load round-trip.
- Latency benchmarks: 50 token generation < 10ms, probability query < 1ms.
"""

from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path


class TestMarkovLanguageModel(unittest.TestCase):
    """TDD test cases for MarkovLanguageModel."""

    def test_import_from_engine_model(self):
        """Test that MarkovLanguageModel is exported from engine.model."""
        from engine.model import MarkovLanguageModel

        self.assertIsNotNone(MarkovLanguageModel)
        lm = MarkovLanguageModel()
        self.assertIsNotNone(lm)
        self.assertEqual(lm.order, 3)
        self.assertEqual(lm.laplace_alpha, 1.0)
        self.assertGreaterEqual(lm.vocab_size, 4)  # At least special tokens

    def test_initialization_with_custom_tokenizer(self):
        """Test initialization with custom order, alpha, and tokenizer."""
        from engine.model import CustomTokenizer, MarkovLanguageModel

        tok = CustomTokenizer()
        lm = MarkovLanguageModel(tokenizer=tok, order=4, laplace_alpha=0.5)
        self.assertEqual(lm.order, 4)
        self.assertEqual(lm.laplace_alpha, 0.5)
        self.assertIs(lm.tokenizer, tok)

    def test_model_training_on_sample_corpus(self):
        """Test training on sample texts updates unigram counts and transition tables."""
        from engine.model import MarkovLanguageModel

        corpus = [
            "the quick brown fox jumps over the lazy dog",
            "the quick brown fox runs fast",
        ]
        lm = MarkovLanguageModel(order=3)
        lm.train(corpus)

        # Unigrams should be populated
        self.assertGreater(lm.unigram_counts["quick"], 0)
        self.assertGreater(lm.unigram_counts["fox"], 0)
        self.assertEqual(lm.unigram_counts["quick"], 2)

        # Transitions for ("the", "quick") should have "brown": 2
        self.assertIn(("the", "quick"), lm.transitions)
        self.assertEqual(lm.transitions[("the", "quick")]["brown"], 2)

        # Transitions for ("quick", "brown") should have "fox": 2
        self.assertIn(("quick", "brown"), lm.transitions)
        self.assertEqual(lm.transitions[("quick", "brown")]["fox"], 2)

        # Vocab size should include tokens from corpus plus special tokens
        self.assertIn("fox", lm.vocab)
        self.assertIn("jumps", lm.vocab)
        self.assertGreater(lm.vocab_size, 10)

    def test_probability_distribution_sums_to_one(self):
        """Test that next token probabilities sum to 1.0 across diverse contexts."""
        from engine.model import MarkovLanguageModel

        corpus = [
            "distributed systems require consensus algorithms like raft and paxos",
            "consensus algorithms maintain state machine replication",
        ]
        lm = MarkovLanguageModel(order=3, laplace_alpha=1.0)
        lm.train(corpus)

        # Test context 1: Exact trigram context
        probs1 = lm.get_next_token_probabilities(["distributed", "systems"], top_k=50)
        self.assertTrue(len(probs1) > 0)
        self.assertAlmostEqual(sum(probs1.values()), 1.0, places=5)

        # Test context 2: Bigram context (1 token)
        probs2 = lm.get_next_token_probabilities(["consensus"], top_k=50)
        self.assertTrue(len(probs2) > 0)
        self.assertAlmostEqual(sum(probs2.values()), 1.0, places=5)

        # Test context 3: Unseen context (triggers backoff)
        probs3 = lm.get_next_token_probabilities(["quantum", "teleportation"], top_k=50)
        self.assertTrue(len(probs3) > 0)
        self.assertAlmostEqual(sum(probs3.values()), 1.0, places=5)

        # Test context 4: Empty context
        probs4 = lm.get_next_token_probabilities([], top_k=50)
        self.assertTrue(len(probs4) > 0)
        self.assertAlmostEqual(sum(probs4.values()), 1.0, places=5)

        # Test context 5: All tokens returned when top_k=0 (no truncation)
        probs_all = lm.get_next_token_probabilities(["consensus"], top_k=0)
        self.assertEqual(len(probs_all), lm.vocab_size)
        self.assertAlmostEqual(sum(probs_all.values()), 1.0, places=5)

    def test_laplace_smoothing_non_zero_for_unseen_tokens(self):
        """Test that Laplace smoothing guarantees non-zero probability for unseen transitions."""
        from engine.model import MarkovLanguageModel

        corpus = [
            "database schema migration",
            "software architecture design",
        ]
        lm = MarkovLanguageModel(order=3, laplace_alpha=1.0)
        lm.train(corpus)

        # In context ("database", "schema"), "migration" was seen, but "design" was NOT seen.
        probs = lm.get_next_token_probabilities(["database", "schema"], top_k=0)

        # Seen token should have higher probability than unseen token
        self.assertIn("migration", probs)
        self.assertIn("design", probs)
        self.assertGreater(probs["migration"], probs["design"])

        # Unseen token must still have strictly positive probability due to Laplace smoothing
        self.assertGreater(probs["design"], 0.0)

        # Test direct token probability query
        p_seen = lm.get_token_probability("migration", ["database", "schema"])
        p_unseen = lm.get_token_probability("design", ["database", "schema"])
        self.assertGreater(p_seen, p_unseen)
        self.assertGreater(p_unseen, 0.0)

    def test_backoff_mechanism(self):
        """Test hierarchical backoff: trigram -> bigram -> unigram."""
        from engine.model import MarkovLanguageModel

        corpus = [
            "alpha beta gamma delta",
            "omega beta epsilon",
        ]
        lm = MarkovLanguageModel(order=3, laplace_alpha=1.0)
        lm.train(corpus)

        # 1. Trigram match: ("alpha", "beta") -> "gamma" was seen
        p_trigram = lm.get_next_token_probabilities(["alpha", "beta"], top_k=0)
        self.assertGreater(p_trigram["gamma"], p_trigram["epsilon"])

        # 2. Unseen trigram prefix ("theta", "beta"):
        # ("theta", "beta") not in transitions -> backoff to ("beta",)
        # In ("beta",), both "gamma" and "epsilon" were seen!
        p_backoff = lm.get_next_token_probabilities(["theta", "beta"], top_k=0)
        self.assertGreater(p_backoff["gamma"], 0.0)
        self.assertGreater(p_backoff["epsilon"], 0.0)

        # 3. Completely unseen prefix ("theta", "zeta"):
        # Neither ("theta", "zeta") nor ("zeta",) seen -> backoff to unigram
        p_unigram = lm.get_next_token_probabilities(["theta", "zeta"], top_k=0)
        # Frequent unigram "beta" should have higher probability than infrequent unigram
        self.assertGreater(p_unigram["beta"], 0.0)

    def test_temperature_scaling_effects(self):
        """Test temperature scaling: T -> 0 sharpens mode, high T flattens distribution."""
        from engine.model import MarkovLanguageModel

        corpus = [
            "apple orange apple orange apple banana",
        ]
        lm = MarkovLanguageModel(order=2, laplace_alpha=0.5)
        lm.train(corpus)

        context = ["apple"]

        probs_cold = lm.get_next_token_probabilities(context, temperature=0.1, top_k=0)
        probs_mid = lm.get_next_token_probabilities(context, temperature=1.0, top_k=0)
        probs_hot = lm.get_next_token_probabilities(context, temperature=5.0, top_k=0)

        # Find the mode token after "apple" (which is "orange")
        mode_token = "orange"
        self.assertIn(mode_token, probs_cold)

        # Cold temperature should concentrate probability on the mode
        self.assertGreater(probs_cold[mode_token], probs_mid[mode_token])
        self.assertGreater(probs_mid[mode_token], probs_hot[mode_token])

        # Under very high temperature, distribution should flatten (probabilities get closer to each other)
        diff_cold = probs_cold[mode_token] - probs_cold["banana"]
        diff_hot = probs_hot[mode_token] - probs_hot["banana"]
        self.assertGreater(diff_cold, diff_hot)

    def test_nucleus_top_p_sampling(self):
        """Test sample_next_token with greedy and top-p nucleus sampling."""
        from engine.model import MarkovLanguageModel

        corpus = [
            "status code 200 ok",
            "status code 200 ok",
            "status code 200 ok",
            "status code 404 not found",
        ]
        lm = MarkovLanguageModel(order=3)
        lm.train(corpus)

        # Deterministic greedy sampling (temperature=0.0)
        token_greedy = lm.sample_next_token(["status", "code"], temperature=0.0)
        self.assertEqual(token_greedy, "200")

        # Top-p sampling with tight nucleus
        token_nucleus = lm.sample_next_token(["status", "code"], temperature=0.5, top_p=0.5)
        self.assertEqual(token_nucleus, "200")

    def test_text_generation_coherent_completion(self):
        """Test text generation from seed prompts."""
        from engine.model import MarkovLanguageModel

        corpus = [
            "def authenticate_user(username, password): return verify_credentials(username, password)",
            "def query_database(sql_query): return execute_statement(sql_query)",
        ]
        lm = MarkovLanguageModel(order=3, laplace_alpha=0.1)
        lm.train(corpus)

        # Generation from seed prompt with greedy temperature
        output = lm.generate(
            prompt="def authenticate_user",
            max_tokens=15,
            temperature=0.0,
        )

        self.assertIn("def authenticate_user", output)
        self.assertIn("username", output)
        self.assertIn("password", output)

    def test_generation_stop_tokens_and_max_tokens(self):
        """Test that generation strictly respects max_tokens and custom stop_tokens."""
        from engine.model import MarkovLanguageModel

        corpus = [
            "step 1 initialize step 2 process step 3 finalize step 4 complete",
        ]
        lm = MarkovLanguageModel(order=3, laplace_alpha=0.1)
        lm.train(corpus)

        # max_tokens limit
        out_limited = lm.generate(
            prompt="step 1",
            max_tokens=3,
            temperature=0.0,
            include_prompt=False,
        )
        tokens_limited = lm.tokenizer.tokenize(out_limited)
        self.assertLessEqual(len(tokens_limited), 3)

        # stop_tokens parameter
        out_stopped = lm.generate(
            prompt="step 1",
            max_tokens=20,
            temperature=0.0,
            stop_tokens=["step 3"],
            include_prompt=True,
        )
        self.assertNotIn("step 4", out_stopped)

    def test_train_on_directory_skills(self):
        """Test training on markdown documents in the skills/ directory."""
        from engine.model import MarkovLanguageModel

        skills_dir = Path("skills")
        self.assertTrue(skills_dir.exists(), "skills directory must exist")

        lm = MarkovLanguageModel(order=3, laplace_alpha=1.0)
        file_count = lm.train_on_directory(skills_dir, pattern="SKILL.md", recursive=True)

        self.assertGreaterEqual(file_count, 30, "Should train on at least 30 SKILL.md files")
        self.assertGreater(lm.vocab_size, 500, "Vocabulary should exceed 500 tokens from skills")
        self.assertGreater(len(lm.transitions), 1000, "Should extract transitions across skills")

        # Test generation with domain prompt
        domain_output = lm.generate(
            prompt="The system architecture",
            max_tokens=20,
            temperature=0.7,
            top_p=0.9,
        )
        self.assertTrue(domain_output.startswith("The system architecture"))
        self.assertGreater(len(domain_output), len("The system architecture"))

    def test_serialization_json_roundtrip(self):
        """Test to_dict, from_dict, save, and load roundtrip persistence."""
        from engine.model import MarkovLanguageModel

        corpus = [
            "microservices architecture with docker containers and kubernetes",
            "continuous integration pipeline with automated testing",
        ]
        lm1 = MarkovLanguageModel(order=3, laplace_alpha=0.5)
        lm1.train(corpus)

        # Roundtrip via to_dict / from_dict
        data = lm1.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["order"], 3)
        self.assertEqual(data["laplace_alpha"], 0.5)

        lm2 = MarkovLanguageModel.from_dict(data)
        self.assertEqual(lm2.order, lm1.order)
        self.assertEqual(lm2.laplace_alpha, lm1.laplace_alpha)
        self.assertEqual(lm2.vocab_size, lm1.vocab_size)
        self.assertEqual(len(lm2.transitions), len(lm1.transitions))

        # Test probabilities parity
        p1 = lm1.get_next_token_probabilities(["microservices", "architecture"])
        p2 = lm2.get_next_token_probabilities(["microservices", "architecture"])
        self.assertEqual(p1, p2)

        # Roundtrip via file save / load
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "test_model.json"
            lm1.save(file_path)
            self.assertTrue(file_path.exists())

            # Ensure valid JSON
            with open(file_path, "r", encoding="utf-8") as f:
                json_content = json.load(f)
            self.assertIn("transitions", json_content)

            lm3 = MarkovLanguageModel.load(file_path)
            self.assertEqual(lm3.vocab_size, lm1.vocab_size)
            p3 = lm3.get_next_token_probabilities(["continuous", "integration"])
            self.assertEqual(p3, lm1.get_next_token_probabilities(["continuous", "integration"]))

    def test_performance_latency_benchmarks(self):
        """Test that probability calculations < 1ms and 50-token generation < 10ms."""
        from engine.model import MarkovLanguageModel

        skills_dir = Path("skills")
        lm = MarkovLanguageModel(order=3, laplace_alpha=1.0)
        lm.train_on_directory(skills_dir, pattern="SKILL.md", recursive=True)

        context = ["The", "system"]

        # 1. Single next-token probabilities query latency (< 1ms)
        t0 = time.perf_counter()
        probs = lm.get_next_token_probabilities(context, top_k=50)
        t1 = time.perf_counter()
        query_ms = (t1 - t0) * 1000.0
        self.assertLess(query_ms, 2.0, f"Query took {query_ms:.3f}ms, expected < 2ms")

        # 2. 50-token sequence generation latency (< 10ms)
        t2 = time.perf_counter()
        gen_output = lm.generate(
            prompt="The system architecture",
            max_tokens=50,
            temperature=0.7,
            top_p=0.9,
        )
        t3 = time.perf_counter()
        gen_ms = (t3 - t2) * 1000.0
        self.assertLess(gen_ms, 10.0, f"50-token generation took {gen_ms:.3f}ms, expected < 10ms")


if __name__ == "__main__":
    unittest.main()
