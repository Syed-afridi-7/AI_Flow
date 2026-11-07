"""Tests for CustomTokenizer in engine.model.tokenizer.

Verifies:
- Symbol preservation (->, ::, {}, [], (), ;, ,, :, .)
- Vocabulary building with frequencies and min_freq / max_vocab_size
- Encode / decode round-trip
- Special tokens handling (<pad>: 0, <unk>: 1, <bos>: 2, <eos>: 3)
- Unknown token fallback to <unk> (ID 1)
- JSON serialization, save / load persistence
- Sub-millisecond performance benchmarks
"""

import json
import tempfile
import time
import unittest
from pathlib import Path


class TestCustomTokenizer(unittest.TestCase):
    """TDD test cases for CustomTokenizer."""

    def test_import_from_engine_model(self):
        """Test that CustomTokenizer can be imported from engine.model."""
        from engine.model import CustomTokenizer
        from engine.model.tokenizer import (
            BOS_ID,
            BOS_TOKEN,
            EOS_ID,
            EOS_TOKEN,
            PAD_ID,
            PAD_TOKEN,
            SPECIAL_TOKENS,
            UNK_ID,
            UNK_TOKEN,
        )

        tokenizer = CustomTokenizer()
        self.assertIsNotNone(tokenizer)
        self.assertEqual(PAD_ID, 0)
        self.assertEqual(UNK_ID, 1)
        self.assertEqual(BOS_ID, 2)
        self.assertEqual(EOS_ID, 3)
        self.assertEqual(PAD_TOKEN, "<pad>")
        self.assertEqual(UNK_TOKEN, "<unk>")
        self.assertEqual(BOS_TOKEN, "<bos>")
        self.assertEqual(EOS_TOKEN, "<eos>")
        self.assertEqual(tokenizer.token_to_id[PAD_TOKEN], 0)
        self.assertEqual(tokenizer.token_to_id[UNK_TOKEN], 1)
        self.assertEqual(tokenizer.token_to_id[BOS_TOKEN], 2)
        self.assertEqual(tokenizer.token_to_id[EOS_TOKEN], 3)
        self.assertEqual(tokenizer.vocab_size, 4)

    def test_symbol_preservation(self):
        """Test that critical code symbols and multi-char operators are preserved."""
        from engine.model.tokenizer import CustomTokenizer

        tok = CustomTokenizer()

        # Multi-char operators and arrows
        code = "def parse(x: int) -> dict: return a == b && c != d || e <= f >= g; => ::"
        tokens = tok.tokenize(code)

        expected_symbols = ["->", "::", "=>", "==", "!=", "<=", ">=", "&&", "||", ";", ":"]
        for sym in expected_symbols:
            self.assertIn(sym, tokens, f"Expected operator '{sym}' to be preserved in {tokens}")

        # Braces, brackets, parentheses
        brackets_code = "{ [ ( ) ] } , ."
        bracket_tokens = tok.tokenize(brackets_code)
        for sym in ["{", "}", "[", "]", "(", ")", ",", "."]:
            self.assertIn(sym, bracket_tokens, f"Expected symbol '{sym}' in {bracket_tokens}")

        # Rust / C++ scope resolution
        cpp_code = "std::collections::HashMap::new()"
        cpp_tokens = tok.tokenize(cpp_code)
        self.assertEqual(
            cpp_tokens,
            ["std", "::", "collections", "::", "HashMap", "::", "new", "(", ")"],
        )

        # JavaScript arrow function and blocks
        js_code = "const handler = () => { return { status: 200 }; };"
        js_tokens = tok.tokenize(js_code)
        self.assertIn("=>", js_tokens)
        self.assertIn("{", js_tokens)
        self.assertIn("}", js_tokens)
        self.assertIn(";", js_tokens)

    def test_case_handling(self):
        """Test lowercase argument in tokenize."""
        from engine.model.tokenizer import CustomTokenizer

        tok = CustomTokenizer()
        text = "Def FooBar() -> Int:"

        case_preserved = tok.tokenize(text, lowercase=False)
        self.assertIn("Def", case_preserved)
        self.assertIn("FooBar", case_preserved)
        self.assertIn("Int", case_preserved)

        case_lowered = tok.tokenize(text, lowercase=True)
        self.assertIn("def", case_lowered)
        self.assertIn("foobar", case_lowered)
        self.assertIn("int", case_lowered)
        self.assertIn("->", case_lowered)  # Symbols remain intact

    def test_vocab_building_with_frequencies(self):
        """Test building vocabulary with frequency filtering and size limits."""
        from engine.model.tokenizer import CustomTokenizer

        tok = CustomTokenizer()
        corpus = [
            "apple banana apple orange apple",
            "banana grape apple banana",
            "cherry pineapple",
        ]

        # Min freq = 2: 'apple' (4), 'banana' (3) qualify; 'orange', 'grape', 'cherry', 'pineapple' have freq 1
        tok.build_vocab(corpus, min_freq=2, max_vocab_size=100)
        self.assertIn("apple", tok.token_to_id)
        self.assertIn("banana", tok.token_to_id)
        self.assertNotIn("orange", tok.token_to_id)
        self.assertNotIn("grape", tok.token_to_id)
        self.assertNotIn("cherry", tok.token_to_id)

        # Special tokens are preserved at indices 0..3
        self.assertEqual(tok.token_to_id["<pad>"], 0)
        self.assertEqual(tok.token_to_id["<unk>"], 1)
        self.assertEqual(tok.token_to_id["<bos>"], 2)
        self.assertEqual(tok.token_to_id["<eos>"], 3)

        # Most frequent token gets ID 4
        self.assertEqual(tok.token_to_id["apple"], 4)
        self.assertEqual(tok.token_to_id["banana"], 5)
        self.assertEqual(tok.vocab_size, 6)

        # Max vocab size capping
        tok_capped = CustomTokenizer()
        tok_capped.build_vocab(corpus, min_freq=1, max_vocab_size=5)
        # 4 special tokens + 1 highest frequency token ('apple') = 5 total
        self.assertEqual(tok_capped.vocab_size, 5)
        self.assertIn("apple", tok_capped.token_to_id)
        self.assertNotIn("banana", tok_capped.token_to_id)

    def test_encode_decode_round_trip(self):
        """Test round trip encoding and decoding."""
        from engine.model.tokenizer import CustomTokenizer

        tok = CustomTokenizer()
        corpus = [
            "hello world this is a test",
            "def add(a: int, b: int) -> int: return a + b;",
            "let items = [1, 2, 3];",
        ]
        tok.build_vocab(corpus, min_freq=1)

        # Natural language round-trip
        text = "hello world this is a test"
        encoded = tok.encode(text)
        decoded = tok.decode(encoded)
        self.assertEqual(decoded, text)

        # Code snippet round-trip
        code_text = "def add(a: int, b: int) -> int: return a + b;"
        code_encoded = tok.encode(code_text)
        code_decoded = tok.decode(code_encoded)
        self.assertEqual(tok.tokenize(code_decoded), tok.tokenize(code_text))

        # Empty string handling
        self.assertEqual(tok.encode(""), [])
        self.assertEqual(tok.decode([]), "")

    def test_special_tokens_handling(self):
        """Test add_special_tokens and skip_special_tokens options."""
        from engine.model.tokenizer import BOS_ID, EOS_ID, PAD_ID, UNK_ID, CustomTokenizer

        tok = CustomTokenizer()
        tok.build_vocab(["hello world"])

        # add_special_tokens adds <bos> at beginning and <eos> at end
        ids = tok.encode("hello world", add_special_tokens=True)
        self.assertEqual(ids[0], BOS_ID)
        self.assertEqual(ids[-1], EOS_ID)
        self.assertEqual(len(ids), 4)

        # skip_special_tokens=True strips framing/padding tokens
        decoded_clean = tok.decode(ids, skip_special_tokens=True)
        self.assertEqual(decoded_clean, "hello world")

        # skip_special_tokens=False keeps <bos> and <eos>
        decoded_raw = tok.decode(ids, skip_special_tokens=False)
        self.assertEqual(decoded_raw, "<bos> hello world <eos>")

        # Padding tokens ignored when skip_special_tokens=True
        padded_ids = [PAD_ID, PAD_ID, ids[1], ids[2], PAD_ID]
        self.assertEqual(tok.decode(padded_ids, skip_special_tokens=True), "hello world")

    def test_unknown_token_fallback(self):
        """Test that unseen tokens map to <unk> (ID 1)."""
        from engine.model.tokenizer import UNK_ID, CustomTokenizer

        tok = CustomTokenizer()
        tok.build_vocab(["hello", "world"])

        # "universe" is unseen, should map to UNK_ID (1)
        encoded = tok.encode("hello universe")
        self.assertEqual(encoded[0], tok.token_to_id["hello"])
        self.assertEqual(encoded[1], UNK_ID)
        self.assertEqual(tok.id_to_token[UNK_ID], "<unk>")

        # Decoding with skip_special_tokens=False renders <unk>
        decoded_raw = tok.decode(encoded, skip_special_tokens=False)
        self.assertEqual(decoded_raw, "hello <unk>")

    def test_json_save_load_persistence(self):
        """Test serialization to dict and JSON file save/load."""
        from engine.model.tokenizer import CustomTokenizer

        tok = CustomTokenizer()
        corpus = [
            "model architecture and vector memory engine",
            "def forward(x: Tensor) -> Tensor: return x * 2;",
        ]
        tok.build_vocab(corpus, min_freq=1)

        # to_dict / from_dict
        d = tok.to_dict()
        self.assertIn("token_to_id", d)
        self.assertIn("id_to_token", d)
        self.assertEqual(d["vocab_size"], tok.vocab_size)

        tok_from_dict = CustomTokenizer.from_dict(d)
        self.assertEqual(tok_from_dict.vocab_size, tok.vocab_size)
        self.assertEqual(tok_from_dict.token_to_id, tok.token_to_id)
        self.assertEqual(tok_from_dict.id_to_token, tok.id_to_token)

        # Save to disk and load
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "sub_dir" / "tokenizer.json"
            tok.save(file_path)
            self.assertTrue(file_path.exists())

            # Validate valid JSON
            with open(file_path, "r", encoding="utf-8") as f:
                loaded_raw = json.load(f)
            self.assertEqual(loaded_raw["vocab_size"], tok.vocab_size)

            loaded_tok = CustomTokenizer.load(file_path)
            self.assertEqual(loaded_tok.vocab_size, tok.vocab_size)
            self.assertEqual(loaded_tok.token_to_id, tok.token_to_id)
            self.assertEqual(loaded_tok.id_to_token, tok.id_to_token)

            # Round trip with loaded tokenizer
            sample = "forward ( x : Tensor ) -> Tensor"
            self.assertEqual(loaded_tok.encode(sample), tok.encode(sample))

    def test_sub_millisecond_benchmark(self):
        """Benchmark tokenization, encoding, and decoding to ensure < 1.0 ms execution."""
        from engine.model.tokenizer import CustomTokenizer

        tok = CustomTokenizer()
        corpus = [
            "def optimize_schema(table_name: str, indexes: list[str]) -> dict:",
            "    # Zero-downtime concurrent indexing",
            "    return {'status': 'optimized', 'table': table_name, 'count': len(indexes)};",
        ]
        tok.build_vocab(corpus, min_freq=1)

        target_text = "def optimize_schema(table_name: str, indexes: list[str]) -> dict: return status;"

        iterations = 200
        start = time.perf_counter()
        for _ in range(iterations):
            tokens = tok.tokenize(target_text)
            encoded = tok.encode(target_text)
            decoded = tok.decode(encoded)
        total_time = time.perf_counter() - start

        avg_ms = (total_time / iterations) * 1000.0
        # Must execute in under 1.0 ms per iteration (typically < 0.05 ms)
        self.assertLess(avg_ms, 1.0, f"Expected < 1.0ms, got {avg_ms:.4f}ms")


if __name__ == "__main__":
    unittest.main()
