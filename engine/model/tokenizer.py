"""Pure-Python Custom Tokenizer for code and natural language text.

Self-contained standard library tokenizer preserving critical syntax
symbols, managing bidirectional vocabulary mapping, and supporting
sub-millisecond encoding/decoding.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

PAD_TOKEN: str = "<pad>"
UNK_TOKEN: str = "<unk>"
BOS_TOKEN: str = "<bos>"
EOS_TOKEN: str = "<eos>"

PAD_ID: int = 0
UNK_ID: int = 1
BOS_ID: int = 2
EOS_ID: int = 3

SPECIAL_TOKENS: dict[str, int] = {
    PAD_TOKEN: PAD_ID,
    UNK_TOKEN: UNK_ID,
    BOS_TOKEN: BOS_ID,
    EOS_TOKEN: EOS_ID,
}

# Compiled regex matching special tokens, multi-character code operators,
# floating point numbers, words/identifiers, and single-character symbols.
_TOKEN_PATTERN = re.compile(
    r"<pad>|<unk>|<bos>|<eos>"
    r"|<!--|-->|\.\.\."
    r"|===|!==|->|=>|::|==|!=|<=|>=|&&|\|\||\+\+|--|\+=|-=|\*=|/=|<<|>>|\*\*|//|:=|\?\?|\?\."
    r"|```|\"\"\"|'''"
    r"|\d+\.\d+"
    r"|\w+"
    r"|\S"
)

_NO_SPACE_BEFORE: frozenset[str] = frozenset({",", ";", ":", ".", "!", "?", ")", "]", "}"})
_NO_SPACE_AFTER: frozenset[str] = frozenset({"(", "[", "{", "@"})


class CustomTokenizer:
    """Bi-directional code and natural language tokenizer.

    Preserves programming language symbols and operators (e.g., ->, ::, =>, ==, !=,
    {}, [], (), ;, ,, :, .), maintains deterministic vocabulary frequencies,
    and supports JSON persistence.
    """

    PAD_TOKEN: str = PAD_TOKEN
    UNK_TOKEN: str = UNK_TOKEN
    BOS_TOKEN: str = BOS_TOKEN
    EOS_TOKEN: str = EOS_TOKEN

    PAD_ID: int = PAD_ID
    UNK_ID: int = UNK_ID
    BOS_ID: int = BOS_ID
    EOS_ID: int = EOS_ID

    SPECIAL_TOKENS: dict[str, int] = SPECIAL_TOKENS

    def __init__(
        self,
        token_to_id: dict[str, int] | None = None,
        id_to_token: dict[int, str] | None = None,
    ) -> None:
        """Initialize tokenizer with existing or default special token vocabularies."""
        if token_to_id is not None and id_to_token is not None:
            self.token_to_id: dict[str, int] = dict(token_to_id)
            self.id_to_token: dict[int, str] = {int(k): v for k, v in id_to_token.items()}
        elif token_to_id is not None:
            self.token_to_id = dict(token_to_id)
            self.id_to_token = {v: k for k, v in token_to_id.items()}
        else:
            self.token_to_id = dict(SPECIAL_TOKENS)
            self.id_to_token = {v: k for k, v in SPECIAL_TOKENS.items()}
        self.token_counts: dict[str, int] = {}

    @property
    def vocab_size(self) -> int:
        """Total number of tokens currently registered in the vocabulary."""
        return len(self.token_to_id)

    @classmethod
    def tokenize(cls, text: str, lowercase: bool = False) -> list[str]:
        """Tokenize natural language text and source code syntax into discrete tokens.

        Preserves multi-char operators (->, ::, =>, ==, !=, <=, >=, &&, ||)
        and symbols ({}, [], (), ;, ,, :, .).
        """
        if not text:
            return []
        if lowercase:
            text = text.lower()
        return _TOKEN_PATTERN.findall(text)

    def build_vocab(
        self,
        corpus: list[str],
        min_freq: int = 1,
        max_vocab_size: int = 10000,
    ) -> None:
        """Build vocabulary from a corpus of texts with frequency filtering.

        Special tokens (<pad>: 0, <unk>: 1, <bos>: 2, <eos>: 3) are always reserved.

        Args:
            corpus: List of text documents/strings to index.
            min_freq: Minimum occurrences required for a token to enter vocabulary.
            max_vocab_size: Maximum vocabulary capacity including special tokens.
        """
        counts: Counter[str] = Counter()
        for text in corpus:
            tokens = self.tokenize(text)
            counts.update(tokens)

        # Reset vocabulary to default special tokens
        self.token_to_id = dict(SPECIAL_TOKENS)
        self.id_to_token = {v: k for k, v in SPECIAL_TOKENS.items()}
        self.token_counts = dict(counts)

        # Filter candidate tokens meeting min_freq, excluding special tokens
        candidates = [
            tok
            for tok, count in counts.items()
            if count >= min_freq and tok not in self.token_to_id
        ]
        # Sort deterministically: highest frequency first, then lexicographically
        candidates.sort(key=lambda tok: (-counts[tok], tok))

        for tok in candidates:
            if len(self.token_to_id) >= max_vocab_size:
                break
            new_id = len(self.token_to_id)
            self.token_to_id[tok] = new_id
            self.id_to_token[new_id] = tok

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        """Map text to integer IDs. Unseen tokens map to <unk> (ID 1).

        Args:
            text: Input string to encode.
            add_special_tokens: If True, wraps token IDs with <bos> and <eos>.
        """
        if not text or not text.strip():
            return []
        tokens = self.tokenize(text)
        unk_id = self.token_to_id.get(UNK_TOKEN, UNK_ID)
        ids = [self.token_to_id.get(tok, unk_id) for tok in tokens]
        if add_special_tokens:
            bos_id = self.token_to_id.get(BOS_TOKEN, BOS_ID)
            eos_id = self.token_to_id.get(EOS_TOKEN, EOS_ID)
            return [bos_id] + ids + [eos_id]
        return ids

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        """Decode integer IDs back to reconstructed text.

        Args:
            ids: List of integer token IDs.
            skip_special_tokens: If True, strips reserved special tokens (<pad>, <unk>, <bos>, <eos>).
        """
        if not ids:
            return ""
        tokens: list[str] = []
        for token_id in ids:
            tok = self.id_to_token.get(token_id, UNK_TOKEN)
            if skip_special_tokens and (tok in self.SPECIAL_TOKENS):
                continue
            tokens.append(tok)
        return self._detokenize(tokens)

    @staticmethod
    def _detokenize(tokens: list[str]) -> str:
        """Reconstruct tokens into formatted string with syntax-aware spacing."""
        if not tokens:
            return ""

        result: list[str] = []
        for i, tok in enumerate(tokens):
            if i == 0:
                result.append(tok)
                continue
            prev = tokens[i - 1]

            if tok in _NO_SPACE_BEFORE:
                result.append(tok)
            elif prev in _NO_SPACE_AFTER:
                result.append(tok)
            elif tok == "::" or prev == "::":
                result.append(tok)
            elif tok == "." or prev == ".":
                if prev == "." and (tok[0].isupper() or not tok.isidentifier()):
                    result.append(" " + tok)
                else:
                    result.append(tok)
            elif tok in ("(", "[") and (prev.isidentifier() or prev in (")", "]")):
                result.append(tok)
            elif (
                (prev == "(" and tok == ")")
                or (prev == "[" and tok == "]")
                or (prev == "{" and tok == "}")
            ):
                result.append(tok)
            else:
                result.append(" " + tok)

        return "".join(result)

    def to_dict(self) -> dict[str, Any]:
        """Serialize tokenizer state to dictionary for JSON persistence."""
        return {
            "token_to_id": self.token_to_id,
            "id_to_token": {str(k): v for k, v in self.id_to_token.items()},
            "vocab_size": self.vocab_size,
            "token_counts": self.token_counts,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CustomTokenizer:
        """Construct tokenizer from serialized dictionary."""
        token_to_id = data.get("token_to_id", dict(SPECIAL_TOKENS))
        raw_id_to_token = data.get("id_to_token")
        if raw_id_to_token is not None:
            id_to_token = {int(k): v for k, v in raw_id_to_token.items()}
        else:
            id_to_token = {int(v): k for k, v in token_to_id.items()}
        tokenizer = cls(token_to_id=token_to_id, id_to_token=id_to_token)
        tokenizer.token_counts = data.get("token_counts", {})
        return tokenizer

    def save(self, path: str | Path) -> None:
        """Save vocabulary and configuration to a JSON file."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str | Path) -> CustomTokenizer:
        """Load vocabulary and configuration from a JSON file."""
        file_path = Path(path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
