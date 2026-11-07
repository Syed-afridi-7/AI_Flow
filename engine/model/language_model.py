"""Pure-Python Statistical Markov Language Model with Laplace Smoothing.

Higher-order n-gram probabilistic language model providing conditional
transition probabilities, hierarchical backoff (trigram -> bigram -> unigram),
add-alpha Laplace smoothing, temperature scaling, and top-p nucleus sampling.
100% Python standard library with zero external dependencies.
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

from engine.model.tokenizer import CustomTokenizer


class MarkovLanguageModel:
    """Probabilistic N-Gram Markov Language Model with Laplace Smoothing.

    Features:
    - Arbitrary n-gram order (defaults to order 3 / trigram).
    - Hierarchical backoff: Order-N -> Bigram -> Unigram -> Uniform.
    - Add-alpha Laplace smoothing to ensure non-zero probability for unseen tokens.
    - Temperature scaling: T -> 0 concentrates on mode; higher T flattens distribution.
    - Top-p (nucleus) stochastic sampling and greedy deterministic decoding.
    - Efficient sub-millisecond next-token predictions and generation (< 10ms for 50 tokens).
    - Standard JSON persistence round-trip.
    """

    def __init__(
        self,
        tokenizer: CustomTokenizer | None = None,
        order: int = 3,
        laplace_alpha: float = 1.0,
    ) -> None:
        """Initialize the Markov Language Model.

        Args:
            tokenizer: CustomTokenizer instance (creates default if None).
            order: N-gram order (e.g. 3 for trigram model using 2 context tokens).
            laplace_alpha: Add-alpha smoothing parameter (default 1.0).
        """
        self.tokenizer: CustomTokenizer = tokenizer if tokenizer is not None else CustomTokenizer()
        self.order: int = max(1, order)
        self.laplace_alpha: float = float(laplace_alpha)

        self.unigram_counts: Counter[str] = Counter()
        self.transitions: dict[tuple[str, ...], Counter[str]] = {}
        self.vocab: set[str] = set(self.tokenizer.token_to_id.keys())
        self._sorted_vocab: list[str] | None = None

    @property
    def vocab_size(self) -> int:
        """Total number of unique tokens registered in the model vocabulary."""
        return len(self.vocab)

    @property
    def sorted_vocab(self) -> list[str]:
        """Pre-sorted list of vocabulary tokens for deterministic fast access."""
        if self._sorted_vocab is None or len(self._sorted_vocab) != len(self.vocab):
            self._sorted_vocab = sorted(self.vocab)
        return self._sorted_vocab

    def reset(self) -> None:
        """Clear all learned counts and transitions while preserving vocabulary."""
        self.unigram_counts.clear()
        self.transitions.clear()
        self.vocab = set(self.tokenizer.token_to_id.keys())
        self._sorted_vocab = None

    def train(self, corpus: list[str]) -> None:
        """Train language model on a collection of text documents.

        Tokenizes each text, updates unigram counts and n-gram transition tables
        across all context lengths from 1 to (order - 1), including start (<bos>)
        and end (<eos>) boundary markers.

        Args:
            corpus: List of text documents/strings to learn transitions from.
        """
        if not corpus:
            return

        bos_token = self.tokenizer.BOS_TOKEN
        eos_token = self.tokenizer.EOS_TOKEN

        for text in corpus:
            if not text:
                continue
            raw_tokens = self.tokenizer.tokenize(text)
            if not raw_tokens:
                continue

            # Ensure all discovered tokens exist in tokenizer vocabulary
            for tok in raw_tokens:
                if tok not in self.tokenizer.token_to_id:
                    new_id = len(self.tokenizer.token_to_id)
                    self.tokenizer.token_to_id[tok] = new_id
                    self.tokenizer.id_to_token[new_id] = tok
                self.vocab.add(tok)

            # Update unigram counts for body tokens and EOS
            self.unigram_counts.update(raw_tokens)
            self.unigram_counts[eos_token] += 1
            self.vocab.add(eos_token)
            self.vocab.add(bos_token)

            # Pad document sequence with (order - 1) BOS markers and 1 EOS marker
            pad_len = self.order - 1
            doc_tokens = ([bos_token] * pad_len) + raw_tokens + [eos_token]

            # Index transitions for all context lengths from 1 to (order - 1)
            for i in range(pad_len, len(doc_tokens)):
                target = doc_tokens[i]
                for k in range(1, self.order):
                    ctx = tuple(doc_tokens[i - k : i])
                    if ctx not in self.transitions:
                        self.transitions[ctx] = Counter()
                    self.transitions[ctx][target] += 1

        self._sorted_vocab = sorted(self.vocab)

    def train_on_directory(
        self,
        dir_path: str | Path,
        pattern: str = "*.md",
        recursive: bool = True,
    ) -> int:
        """Read all matching files from a directory and train on their contents.

        Args:
            dir_path: Path to directory containing training files.
            pattern: Glob pattern to filter target files (default '*.md').
            recursive: If True, recursively searches subdirectories.

        Returns:
            Number of successfully processed files.
        """
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            return 0

        files = sorted(path.rglob(pattern) if recursive else path.glob(pattern))
        corpus: list[str] = []
        processed_count = 0

        for file_path in files:
            if not file_path.is_file():
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                if content.strip():
                    corpus.append(content)
                    processed_count += 1
            except Exception:
                continue

        if corpus:
            self.train(corpus)

        return processed_count

    def _resolve_context_counts(self, context: list[str]) -> Counter[str]:
        """Resolve transition counts using hierarchical backoff.

        Attempts full (order - 1) context tuple, backing off to shorter suffixes,
        then BOS context for empty inputs, and finally unigram counts.
        """
        max_ctx_len = self.order - 1

        if context:
            ctx_tokens = context[-max_ctx_len:]
            # Try progressively shorter suffix tuples down to length 1
            for length in range(len(ctx_tokens), 0, -1):
                ctx_tuple = tuple(ctx_tokens[-length:])
                if ctx_tuple in self.transitions and len(self.transitions[ctx_tuple]) > 0:
                    return self.transitions[ctx_tuple]
        else:
            # Empty context: check for initial BOS transition
            bos_tuple = (self.tokenizer.BOS_TOKEN,) * max_ctx_len
            if bos_tuple in self.transitions and len(self.transitions[bos_tuple]) > 0:
                return self.transitions[bos_tuple]

        return self.unigram_counts

    def get_token_probability(
        self,
        token: str,
        context: list[str],
        temperature: float = 1.0,
    ) -> float:
        """Compute the Laplace smoothed conditional probability for a single token.

        Args:
            token: The candidate next token string.
            context: List of preceding tokens.
            temperature: Sampling temperature scaling factor.

        Returns:
            Smoothed conditional probability P(token | context) >= 0.0.
        """
        if self.vocab_size == 0:
            return 0.0

        counts = self._resolve_context_counts(context)
        alpha = max(0.0, self.laplace_alpha)
        total_counts = sum(counts.values())
        denom = total_counts + (alpha * self.vocab_size)
        if denom <= 0:
            return 1.0 / self.vocab_size

        token_count = counts.get(token, 0)
        base_p = (token_count + alpha) / denom

        if temperature == 1.0:
            return base_p

        # For temperature != 1.0, probability relative to vocabulary
        if temperature <= 1e-5:
            max_count = max(counts.values()) if counts else 0
            return 1.0 if token_count == max_count and max_count > 0 else 0.0

        return base_p ** (1.0 / temperature)

    def get_next_token_probabilities(
        self,
        context: list[str],
        temperature: float = 1.0,
        top_k: int = 50,
    ) -> dict[str, float]:
        """Compute Laplace smoothed probability distribution over candidate next tokens.

        Args:
            context: List of preceding token strings.
            temperature: Sampling temperature (T -> 0 sharpens mode, high T flattens).
            top_k: Number of highest-probability tokens to retain (0 or None for full vocab).

        Returns:
            Dictionary mapping candidate tokens to normalized probabilities summing to 1.0.
        """
        vocab_size = self.vocab_size
        if vocab_size == 0:
            return {}

        counts = self._resolve_context_counts(context)
        alpha = max(0.0, self.laplace_alpha)

        # Select candidate tokens fast without scanning all vocabulary when top_k is small
        if top_k is None or top_k <= 0 or top_k >= vocab_size:
            candidates = self.sorted_vocab
        else:
            seen_tokens = [tok for tok, _ in counts.most_common(top_k)]
            if len(seen_tokens) < top_k:
                seen_set = set(seen_tokens)
                needed = top_k - len(seen_tokens)
                unseen: list[str] = []
                for tok in self.sorted_vocab:
                    if tok not in seen_set:
                        unseen.append(tok)
                        if len(unseen) == needed:
                            break
                candidates = seen_tokens + unseen
            else:
                candidates = seen_tokens[:top_k]

        if not candidates:
            return {}

        # Greedy argmax mode for near-zero temperature
        if temperature <= 1e-5:
            best_token = min(candidates, key=lambda w: (-counts.get(w, 0), w))
            pairs = [(w, 1.0 if w == best_token else 0.0) for w in candidates]
            pairs.sort(key=lambda x: (-x[1], x[0]))
            limit = top_k if (top_k is not None and top_k > 0) else len(pairs)
            return {w: weight for w, weight in pairs[:limit]}

        # Temperature scaling
        # (counts[w] + alpha) / denom raised to (1/T) normalized over candidates
        if temperature == 1.0:
            weights = [(counts.get(w, 0) + alpha) for w in candidates]
        else:
            inv_t = 1.0 / temperature
            # Scale by max_c to avoid overflow/underflow
            max_c = max((counts.get(w, 0) for w in candidates), default=0) + alpha
            if max_c <= 0:
                max_c = 1.0
            weights = [((counts.get(w, 0) + alpha) / max_c) ** inv_t for w in candidates]

        pairs = sorted(zip(candidates, weights), key=lambda x: (-x[1], x[0]))
        limit = top_k if (top_k is not None and top_k > 0) else len(pairs)
        selected_pairs = pairs[:limit]
        total_weight = sum(w for _, w in selected_pairs)
        if total_weight <= 0.0:
            uniform_p = 1.0 / len(selected_pairs)
            return {w: uniform_p for w, _ in selected_pairs}

        return {w: weight / total_weight for w, weight in selected_pairs}

    def sample_next_token(
        self,
        context: list[str],
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
    ) -> str:
        """Sample a candidate token using temperature scaling and top-p nucleus pruning.

        Args:
            context: List of preceding tokens.
            temperature: Sampling temperature.
            top_p: Cumulative probability threshold for nucleus filtering.
            top_k: Candidate pool limit before nucleus filtering.

        Returns:
            Sampled token string.
        """
        probs = self.get_next_token_probabilities(
            context,
            temperature=temperature,
            top_k=top_k,
        )
        if not probs:
            return self.tokenizer.UNK_TOKEN

        if temperature <= 1e-5:
            return max(probs, key=lambda k: probs[k])

        sorted_candidates = sorted(probs.items(), key=lambda kv: (-kv[1], kv[0]))
        nucleus_tokens: list[str] = []
        nucleus_weights: list[float] = []
        cumulative_prob = 0.0

        for tok, p in sorted_candidates:
            nucleus_tokens.append(tok)
            nucleus_weights.append(p)
            cumulative_prob += p
            if cumulative_prob >= top_p:
                break

        if len(nucleus_tokens) == 1:
            return nucleus_tokens[0]

        return random.choices(nucleus_tokens, weights=nucleus_weights, k=1)[0]

    def generate(
        self,
        prompt: str,
        max_tokens: int = 50,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop_tokens: list[str] | None = None,
        include_prompt: bool = True,
    ) -> str:
        """Generate text completions from a seed prompt.

        Args:
            prompt: Seed input text.
            max_tokens: Maximum number of new tokens to synthesize.
            temperature: Sampling temperature.
            top_p: Nucleus pruning threshold.
            stop_tokens: Optional list of strings that halt generation upon occurrence.
            include_prompt: If True, prepends original prompt to returned decoded text.

        Returns:
            Reconstructed formatted text.
        """
        if self.vocab_size == 0 or max_tokens <= 0:
            return prompt if include_prompt else ""

        prompt_tokens = self.tokenizer.tokenize(prompt)
        curr_tokens = list(prompt_tokens)
        generated_tokens: list[str] = []

        stop_set = set(stop_tokens or [])
        stop_set.add(self.tokenizer.EOS_TOKEN)

        for _ in range(max_tokens):
            next_token = self.sample_next_token(
                curr_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            if not next_token or next_token in stop_set:
                break

            generated_tokens.append(next_token)
            curr_tokens.append(next_token)

            # Check multi-token or joined stop phrase
            if stop_tokens:
                combined_tail = " ".join(generated_tokens)
                if any(st in combined_tail for st in stop_tokens):
                    break

        tokens_to_decode = (prompt_tokens + generated_tokens) if include_prompt else generated_tokens
        token_ids = [
            self.tokenizer.token_to_id.get(tok, self.tokenizer.UNK_ID)
            for tok in tokens_to_decode
        ]
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def to_dict(self) -> dict[str, Any]:
        """Serialize model parameters and transition counts to dictionary."""
        return {
            "order": self.order,
            "laplace_alpha": self.laplace_alpha,
            "tokenizer": self.tokenizer.to_dict(),
            "unigram_counts": dict(self.unigram_counts),
            "transitions": [
                {"context": list(ctx), "counts": dict(counts)}
                for ctx, counts in self.transitions.items()
            ],
            "vocab": sorted(self.vocab),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MarkovLanguageModel:
        """Construct a MarkovLanguageModel instance from serialized dictionary."""
        tok_data = data.get("tokenizer")
        tokenizer = CustomTokenizer.from_dict(tok_data) if tok_data else CustomTokenizer()

        lm = cls(
            tokenizer=tokenizer,
            order=data.get("order", 3),
            laplace_alpha=data.get("laplace_alpha", 1.0),
        )

        lm.unigram_counts = Counter(data.get("unigram_counts", {}))

        raw_transitions = data.get("transitions", [])
        if isinstance(raw_transitions, list):
            for entry in raw_transitions:
                ctx = tuple(entry["context"])
                lm.transitions[ctx] = Counter(entry["counts"])
        elif isinstance(raw_transitions, dict):
            for k, v in raw_transitions.items():
                if isinstance(k, tuple):
                    ctx = k
                else:
                    try:
                        parsed = json.loads(k)
                        ctx = tuple(parsed) if isinstance(parsed, list) else (k,)
                    except Exception:
                        ctx = tuple(k.split(" "))
                lm.transitions[ctx] = Counter(v)

        if "vocab" in data:
            lm.vocab = set(data["vocab"])
        else:
            lm.vocab = set(lm.tokenizer.token_to_id.keys())

        lm._sorted_vocab = sorted(lm.vocab)
        return lm

    def save(self, path: str | Path) -> None:
        """Save language model parameters and transition counts to a JSON file."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str | Path) -> MarkovLanguageModel:
        """Load language model parameters and transition counts from a JSON file."""
        file_path = Path(path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
