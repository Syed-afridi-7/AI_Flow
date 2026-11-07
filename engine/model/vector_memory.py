"""Pure-Python TF-IDF Semantic Vector Memory with Cosine Similarity Retrieval.

Self-contained standard library vector space model providing sub-millisecond
in-memory indexing, smooth IDF calculation, L2-normalized vector embeddings,
and cosine similarity ranking across workspace documents and skills.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from engine.model.tokenizer import CustomTokenizer

DEFAULT_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between",
        "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do",
        "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from",
        "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd",
        "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his",
        "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
        "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
        "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll",
        "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the",
        "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
        "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
        "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've",
        "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
        "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
        "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    }
)


@dataclass
class MemoryMatch:
    """Ranked match result from a semantic vector memory query."""

    doc_id: str
    score: float
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class VectorMemory:
    """TF-IDF Vector Space Model and Cosine Similarity retrieval engine.

    Provides in-memory document indexing, smooth IDF calculation, L2-normalized
    vector embeddings, and deterministic cosine similarity ranking in pure Python.
    """

    DEFAULT_STOPWORDS: frozenset[str] = DEFAULT_STOPWORDS

    def __init__(
        self,
        tokenizer: CustomTokenizer | None = None,
        stopwords: set[str] | None = None,
    ) -> None:
        """Initialize VectorMemory with a tokenizer and optional stopwords set."""
        self.tokenizer: CustomTokenizer = tokenizer if tokenizer is not None else CustomTokenizer()
        if stopwords is None:
            self.stopwords: set[str] = set(DEFAULT_STOPWORDS)
        else:
            self.stopwords = {w.lower() for w in stopwords}

        self.documents: dict[str, dict[str, Any]] = {}
        self.doc_freqs: dict[str, int] = {}
        self._doc_vectors: dict[str, dict[str, float]] = {}
        self._dirty: bool = False

    @property
    def document_count(self) -> int:
        """Total number of indexed documents in the corpus."""
        return len(self.documents)

    def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Index a document into vector memory.

        Tracks term frequencies and corpus-level document frequencies.
        If doc_id already exists, updates document in-place.
        """
        if doc_id in self.documents:
            old_unique = set(self.documents[doc_id]["tokens"])
            for term in old_unique:
                self.doc_freqs[term] -= 1
                if self.doc_freqs[term] <= 0:
                    del self.doc_freqs[term]

        raw_tokens = self.tokenizer.tokenize(content, lowercase=True)
        if self.stopwords:
            tokens = [t for t in raw_tokens if t not in self.stopwords]
        else:
            tokens = raw_tokens

        unique_terms = set(tokens)
        for term in unique_terms:
            self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.documents[doc_id] = {
            "doc_id": doc_id,
            "content": content,
            "metadata": dict(metadata) if metadata is not None else {},
            "tokens": tokens,
            "term_counts": Counter(tokens),
            "total_tokens": len(tokens),
        }
        self._dirty = True

    def index_directory(
        self,
        dir_path: str | Path,
        pattern: str = "*.md",
        recursive: bool = True,
    ) -> int:
        """Scan directory, read matching files, and index using relative path as doc_id.

        Returns total count of newly indexed documents.
        """
        root = Path(dir_path)
        if not root.is_dir():
            return 0
        count = 0
        files = root.rglob(pattern) if recursive else root.glob(pattern)
        for file_path in sorted(files):
            if file_path.is_file():
                try:
                    rel_path = file_path.relative_to(root).as_posix()
                    content = file_path.read_text(encoding="utf-8")
                    self.add_document(
                        doc_id=rel_path,
                        content=content,
                        metadata={
                            "path": str(file_path.resolve()),
                            "rel_path": rel_path,
                            "filename": file_path.name,
                        },
                    )
                    count += 1
                except (UnicodeDecodeError, OSError):
                    continue
        return count

    def compute_tf(self, tokens: list[str]) -> dict[str, float]:
        """Compute Term Frequency: count(t) / total_tokens."""
        if not tokens:
            return {}
        total = len(tokens)
        counts = Counter(tokens)
        return {t: count / total for t, count in counts.items()}

    def compute_idf(self, token: str) -> float:
        """Compute smooth Inverse Document Frequency: math.log((1 + N) / (1 + doc_freq(t))) + 1.0."""
        n_docs = len(self.documents)
        doc_freq = self.doc_freqs.get(token, 0)
        return math.log((1 + n_docs) / (1 + doc_freq)) + 1.0

    def compute_tf_idf(
        self,
        tokens: list[str],
        normalize: bool = True,
    ) -> dict[str, float]:
        """Compute TF-IDF weights vector for tokens.

        Optionally L2 normalizes vector so Euclidean length equals 1.0.
        """
        if not tokens:
            return {}
        tf_map = self.compute_tf(tokens)
        raw_weights = {
            token: tf_val * self.compute_idf(token)
            for token, tf_val in tf_map.items()
        }
        if not normalize:
            return raw_weights

        norm = math.sqrt(sum(w * w for w in raw_weights.values()))
        if norm == 0.0:
            return {k: 0.0 for k in raw_weights}
        return {k: v / norm for k, v in raw_weights.items()}

    @staticmethod
    def cosine_similarity(
        vec1: dict[str, float],
        vec2: dict[str, float],
    ) -> float:
        """Calculate cosine similarity between two sparse vector dictionaries.

        Computes dot product over common keys and divides by L2 norms:
        sim(vec1, vec2) = dot(vec1, vec2) / (norm(vec1) * norm(vec2))
        Returns 0.0 if either norm is zero.
        """
        if not vec1 or not vec2:
            return 0.0
        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        if len(vec1) > len(vec2):
            vec1, vec2 = vec2, vec1

        dot = sum(v * vec2[k] for k, v in vec1.items() if k in vec2)
        score = dot / (norm1 * norm2)
        return max(-1.0, min(1.0, score))

    def _ensure_doc_vectors(self) -> None:
        """Lazily recompute cached document vectors when index is dirty."""
        if self._dirty:
            self._doc_vectors = {
                doc_id: self.compute_tf_idf(doc["tokens"])
                for doc_id, doc in self.documents.items()
            }
            self._dirty = False

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> list[MemoryMatch]:
        """Query indexed documents using TF-IDF cosine similarity.

        Args:
            query_text: Natural language or code search query.
            top_k: Maximum number of matches to return.
            threshold: Minimum similarity score threshold.
                       If 0.0, only matches with score > 0.0 are returned.
                       If < 0.0, all documents are returned.
                       If > 0.0, only matches with score >= threshold are returned.

        Returns:
            List of MemoryMatch objects sorted descending by score.
        """
        if not query_text or not query_text.strip() or not self.documents:
            return []

        raw_tokens = self.tokenizer.tokenize(query_text, lowercase=True)
        if self.stopwords:
            query_tokens = [t for t in raw_tokens if t not in self.stopwords]
        else:
            query_tokens = raw_tokens

        if not query_tokens:
            return []

        query_vec = self.compute_tf_idf(query_tokens)
        self._ensure_doc_vectors()

        scored: list[MemoryMatch] = []
        for doc_id, doc in self.documents.items():
            doc_vec = self._doc_vectors.get(doc_id)
            if not doc_vec:
                continue
            sim = self.cosine_similarity(query_vec, doc_vec)

            if threshold < 0.0:
                passes = True
            elif threshold == 0.0:
                passes = sim > 0.0
            else:
                passes = sim >= threshold

            if passes:
                scored.append(
                    MemoryMatch(
                        doc_id=doc_id,
                        score=sim,
                        content=doc["content"],
                        metadata=dict(doc["metadata"]),
                    )
                )

        scored.sort(key=lambda m: (-m.score, m.doc_id))
        return scored[:top_k]

    def to_dict(self) -> dict[str, Any]:
        """Serialize vector memory state to JSON-compatible dictionary."""
        return {
            "tokenizer": self.tokenizer.to_dict(),
            "stopwords": sorted(list(self.stopwords)),
            "documents": {
                doc_id: {
                    "doc_id": doc["doc_id"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "tokens": doc["tokens"],
                    "total_tokens": doc["total_tokens"],
                }
                for doc_id, doc in self.documents.items()
            },
            "doc_freqs": dict(self.doc_freqs),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VectorMemory:
        """Construct VectorMemory instance from serialized dictionary."""
        tok_data = data.get("tokenizer")
        tokenizer = CustomTokenizer.from_dict(tok_data) if tok_data else None
        stopwords_list = data.get("stopwords")
        stopwords = set(stopwords_list) if stopwords_list is not None else None
        vm = cls(tokenizer=tokenizer, stopwords=stopwords)

        raw_docs = data.get("documents", {})
        if isinstance(raw_docs, list):
            for doc in raw_docs:
                vm.add_document(
                    doc_id=doc["doc_id"],
                    content=doc["content"],
                    metadata=doc.get("metadata", {}),
                )
        else:
            for doc_id, doc in raw_docs.items():
                tokens = doc.get("tokens")
                if tokens is None:
                    vm.add_document(
                        doc_id=doc_id,
                        content=doc["content"],
                        metadata=doc.get("metadata", {}),
                    )
                else:
                    vm.documents[doc_id] = {
                        "doc_id": doc_id,
                        "content": doc.get("content", ""),
                        "metadata": doc.get("metadata", {}),
                        "tokens": tokens,
                        "term_counts": Counter(tokens),
                        "total_tokens": doc.get("total_tokens", len(tokens)),
                    }
            if "doc_freqs" in data:
                vm.doc_freqs = dict(data["doc_freqs"])
            else:
                doc_freqs: dict[str, int] = {}
                for doc in vm.documents.values():
                    for term in set(doc["tokens"]):
                        doc_freqs[term] = doc_freqs.get(term, 0) + 1
                vm.doc_freqs = doc_freqs

        vm._dirty = True
        return vm

    def save(self, path: str | Path) -> None:
        """Save vector memory corpus to a JSON file."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str | Path) -> VectorMemory:
        """Load vector memory corpus from a JSON file."""
        file_path = Path(path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
