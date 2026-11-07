"""Hybrid Neuro-Symbolic AI Model Engine.

Provides from-scratch, pure Python standard library components:
- CustomTokenizer: Code and natural language tokenizer.
- VectorMemory: TF-IDF vector space semantic memory.
- MarkovLanguageModel: Probabilistic n-gram language model with Laplace smoothing.
- NeuroSymbolicSynthesizer: Dynamic context-aware generation engine.
"""

from engine.model.tokenizer import CustomTokenizer
from engine.model.vector_memory import MemoryMatch, VectorMemory

__all__ = [
    "CustomTokenizer",
    "VectorMemory",
    "MemoryMatch",
    "MarkovLanguageModel",
    "NeuroSymbolicSynthesizer",
]

try:
    from engine.model.language_model import MarkovLanguageModel  # type: ignore
except ImportError:
    MarkovLanguageModel = None  # type: ignore

try:
    from engine.model.synthesizer import NeuroSymbolicSynthesizer  # type: ignore
except ImportError:
    NeuroSymbolicSynthesizer = None  # type: ignore
