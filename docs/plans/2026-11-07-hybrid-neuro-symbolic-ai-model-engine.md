# Hybrid Neuro-Symbolic AI Model Engine Implementation Plan

> **For Claude / Pair Programmer:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a 100% self-contained, from-scratch AI model and semantic memory engine in pure Python standard library to power dynamic, context-aware generation across AI_Flow's 60 agents.

**Architecture:** Pure Python standard library (`math`, `collections`, `re`, `ast`, `dataclasses`, `pathlib`, `json`, `unittest`). Consists of `CustomTokenizer`, `VectorMemory` (TF-IDF vector space with cosine similarity search), `MarkovLanguageModel` (n-gram statistical sequence modeling with Laplace smoothing), and `NeuroSymbolicSynthesizer` integrating memory retrieval and parametric AST generation.

**Tech Stack:** Python 3.10+ Standard Library (zero external dependencies).

---

## Proposed Changes

Grouped by component layer and ordered logically.

### Component 1: Custom Tokenizer (`engine/model/tokenizer.py`)

#### [NEW] `engine/model/__init__.py`
Exposes the public interfaces of the model package: `CustomTokenizer`, `VectorMemory`, `MarkovLanguageModel`, and `NeuroSymbolicSynthesizer`.

#### [NEW] `engine/model/tokenizer.py`
Tokenizes natural language and programming source code, preserving syntax symbols (`->`, `::`, `{}`, `[]`), managing bidirectional vocabulary (`token_to_id`, `id_to_token`), and handling frequencies.

#### [NEW] `tests/test_model_tokenizer.py`
TDD unit tests verifying tokenization round-trip, symbol preservation, and vocabulary mapping.

---

### Component 2: Semantic Vector Memory (`engine/model/vector_memory.py`)

#### [NEW] `engine/model/vector_memory.py`
Pure-Python TF-IDF vector space model with cosine similarity search:
- Computes Term Frequency (TF) and Inverse Document Frequency (IDF) using standard library `math.log` and `math.sqrt`.
- Indexes local workspace documents, past artifacts, and `skills/*/SKILL.md` files in memory.
- Performs top-$k$ nearest neighbor query matching against prompt vectors.

#### [NEW] `tests/test_model_vector_memory.py`
Unit tests verifying TF-IDF mathematical correctness, cosine similarity ranking, zero-division safety, and semantic ranking on skills.

---

### Component 3: Statistical Markov Language Model (`engine/model/language_model.py`)

#### [NEW] `engine/model/language_model.py`
Higher-order n-gram probabilistic language model:
- Conditional transition probability distribution calculation $P(w_i | w_{i-1}, w_{i-2})$.
- Laplace add-1 smoothing to guarantee non-zero probability on unseen tokens.
- Temperature-scaled stochastic sampling ($T \in [0.1, 1.0]$) and greedy beam search.

#### [NEW] `tests/test_model_language_model.py`
Unit tests verifying probability normalization (sum to 1.0), temperature variance, and coherent phrase synthesis.

---

### Component 4: Neuro-Symbolic Synthesizer & Generator Integration (`engine/model/synthesizer.py`)

#### [NEW] `engine/model/synthesizer.py`
`NeuroSymbolicSynthesizer` that unifies semantic memory retrieval, probabilistic sequence generation, and structural AST code synthesis.
- Integrates with `BaseGenerator` in `engine/core/base.py`.
- Provides `.repair(content, blockers)` method to dynamically fix AST/validator violations.

#### [MODIFY] `engine/core/base.py`
Add optional model synthesis helper to `BaseGenerator`.

#### [NEW] `tests/test_model_synthesizer.py`
Unit tests verifying dynamic content enrichment and automated blocker remediation.

---

### Component 5: Integration & Full Verification

#### [MODIFY] `tests/test_all_60_agents.py`
Ensure all 30 skills and 60 agents execute seamlessly with the new model engine.

---

## Verification Plan

### Automated Tests
1. Model Unit Tests: `python -m unittest discover -s tests -p "test_model_*.py"`
2. Full Integration Suite: `python -m unittest discover -s tests -p "test_*.py"`
3. CLI List & Run: `python -m engine.cli --skill backend-schema --input "E-commerce platform" --mode dual`
4. Validation Parity: `node scripts/validate.js` & `powershell -File scripts/validate.ps1`

### Manual Verification
- Verify sub-millisecond execution times for all model queries.
- Verify zero network traffic and zero third-party dependencies.
- Inspect synthesized deliverables for richer vocabulary and domain precision.
