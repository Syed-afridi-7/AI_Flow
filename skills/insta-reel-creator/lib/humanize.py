#!/usr/bin/env python3
r"""
humanize.py - Strip machine fingerprints, robotic jargon, and AI slop out of content drafts.
Modularized from E:\Insta_Reel for AI_Flow growth & creator skills.
"""

import json
import os
import re
import unicodedata

DEFAULT_SLOP_REPLACEMENTS = {
    r"\bdelve(?:\s+into)?\b": "explore",
    r"\bgame-?changer\b": "breakthrough",
    r"\brevolutionize\b": "transform",
    r"\btestament(?:\s+to|\s+of)?\b": "proof",
    r"\bbeacon\b": "example",
    r"\btapestry\b": "mix",
    r"\bleverage\b": "use",
    r"\bpivotal\b": "key",
    r"\bparamount\b": "critical",
    r"\bseamlessly\b": "smoothly",
    r"\bholistic\b": "complete",
    r"\bmultifaceted\b": "complex",
    r"\bcutting-?edge\b": "modern",
    r"\brobust\b": "reliable",
    r"\bdelve\b": "dive",
    r"\bunleash\b": "unlock",
    r"\bharness\b": "use",
    r"\bvibrant\b": "active",
}

TYPOGRAPHIC_CLEANUPS = [
    (r"\s*—\s*", ", "),  # em dash -> comma
    (r"\s*–\s*(?=\d)", "-"),  # en dash between numbers -> hyphen
    (r"\s+–\s+", ", "),
    (r"[“”]", '"'),
    (r"[‘’]", "'"),
    (r"…", "..."),
]


def strip_invisible_characters(text: str) -> str:
    """Purge zero-width joiners, soft hyphens, BOMs, and Unicode control characters."""
    # Strip common zero-width and formatting codepoints
    pattern = r"[\u200B\u200C\u200D\u2060\uFEFF\u00AD\u180E\u061C\u200E\u200F]"
    text = re.sub(pattern, "", text)
    # Filter any remaining Unicode Cf (format) characters
    return "".join(c for c in text if unicodedata.category(c) != "Cf")


def normalize_typography(text: str) -> str:
    """Normalize em-dashes, en-dashes, curly quotes, and ellipsis."""
    for pattern, replacement in TYPOGRAPHIC_CLEANUPS:
        text = re.sub(pattern, replacement, text)
    # Clean up double punctuation
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*\n", "\n", text)
    return text


def sanitize_slop(text: str) -> str:
    """Purge AI slop words and buzzwords, preserving capitalization and readability."""
    text = strip_invisible_characters(text)
    text = normalize_typography(text)

    for pattern, replacement in DEFAULT_SLOP_REPLACEMENTS.items():
        text = re.sub(
            pattern,
            lambda m: replacement.capitalize() if m.group(0)[0].isupper() else replacement,
            text,
            flags=re.IGNORECASE,
        )

    # Clean double spaces and punctuation gaps
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def humanize(text: str) -> str:
    """Strip machine tells and return humanized text."""
    return sanitize_slop(text)


def check_slop_density(text: str) -> dict:
    """Calculate a human quality score and list detected buzzwords."""
    findings = []
    text_lower = text.lower()
    for pattern in DEFAULT_SLOP_REPLACEMENTS:
        matches = re.findall(pattern, text_lower)
        if matches:
            findings.extend(matches)

    # Count em dashes or curly quotes
    ai_tells = len(re.findall(r"[—…“”‘’]", text))
    slop_count = len(findings) + ai_tells

    # Base score of 100, deducting 5 points per slop occurrence
    score = max(0, 100 - (slop_count * 5))
    return {
        "score": score,
        "slop_count": slop_count,
        "findings": findings,
        "ai_tells_count": ai_tells,
    }
