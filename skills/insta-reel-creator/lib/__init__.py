"""
insta-reel-creator library package.
Provides modularized utilities for hook scoring, beat sheet generation,
humanizing/slop sanitization, and topic memory.
"""

from .hookscore import score_hook
from .beats import generate_beat_sheet, calculate_5_beat_timing
from .humanize import sanitize_slop, humanize
from .memory import TopicMemory

__all__ = [
    "score_hook",
    "generate_beat_sheet",
    "calculate_5_beat_timing",
    "sanitize_slop",
    "humanize",
    "TopicMemory",
]
