import ast
import re
from typing import Optional
from engine.core.types import Blocker, Severity


def validate_python_syntax(code: str) -> list[Blocker]:
    """Parse python code using standard library ast to detect syntax errors."""
    try:
        ast.parse(code)
        return []
    except SyntaxError as e:
        return [
            Blocker(
                rule_id="AST_SYNTAX_ERROR",
                message=f"SyntaxError: {e.msg}",
                severity=Severity.BLOCKER,
                line_number=e.lineno,
                remediation="Fix Python syntax error at indicated line."
            )
        ]


def scan_security_risks(code: str) -> list[Blocker]:
    """Scan python code for common security vulnerabilities (hardcoded secrets, eval, SQLi)."""
    blockers: list[Blocker] = []

    # 1. Hardcoded API keys / secrets
    secret_patterns = [
        (r'["\'](sk-[a-zA-Z0-9_-]{20,})["\']', "SEC_HARDCODED_KEY", "Potential hardcoded API key detected."),
        (r'["\'](ghp_[a-zA-Z0-9]{30,})["\']', "SEC_HARDCODED_KEY", "Potential GitHub Personal Access Token detected."),
        (r'["\'](xox[baprs]-[a-zA-Z0-9-]{20,})["\']', "SEC_HARDCODED_KEY", "Potential Slack token detected."),
        (r'(password|secret|apikey|access_token)\s*=\s*["\'][^"\']{8,}["\']', "SEC_HARDCODED_KEY", "Potential hardcoded credentials detected.")
    ]
    for pattern, rule_id, msg in secret_patterns:
        match = re.search(pattern, code, re.IGNORECASE)
        if match:
            lineno = code[:match.start()].count("\n") + 1
            blockers.append(Blocker(
                rule_id=rule_id,
                message=msg,
                severity=Severity.BLOCKER,
                line_number=lineno,
                remediation="Extract secret to an environment variable or secret manager."
            ))

    # 2. Dangerous calls (eval, exec)
    dangerous_calls = [
        (r'\beval\s*\(', "SEC_DANGEROUS_EVAL", "Use of dangerous eval() function."),
        (r'\bexec\s*\(', "SEC_DANGEROUS_EXEC", "Use of dangerous exec() function."),
    ]
    for pattern, rule_id, msg in dangerous_calls:
        match = re.search(pattern, code)
        if match:
            lineno = code[:match.start()].count("\n") + 1
            blockers.append(Blocker(
                rule_id=rule_id,
                message=msg,
                severity=Severity.BLOCKER,
                line_number=lineno,
                remediation="Avoid eval/exec; use safe parsing or explicit dispatchers."
            ))

    # 3. SQL string interpolation
    sqli_pattern = r'(f["\'].*SELECT\s+.*FROM\s+.*\{.*\}|f["\'].*INSERT\s+INTO\s+.*\{.*\}|f["\'].*UPDATE\s+.*SET\s+.*\{.*\})'
    match = re.search(sqli_pattern, code, re.IGNORECASE)
    if match:
        lineno = code[:match.start()].count("\n") + 1
        blockers.append(Blocker(
            rule_id="SEC_SQL_INJECTION",
            message="Unsafe SQL string formatting detected.",
            severity=Severity.BLOCKER,
            line_number=lineno,
            remediation="Use parameterized queries or ORM binds instead of f-string SQL."
        ))

    return blockers


CONVENTIONAL_COMMIT_TYPES = {
    "feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"
}

def check_conventional_commit(message: str) -> tuple[bool, list[str]]:
    """Verify that a commit message follows the Conventional Commits specification."""
    errors = []
    lines = message.strip().splitlines()
    if not lines:
        return False, ["Commit message cannot be empty."]

    header = lines[0].strip()
    match = re.match(r'^([a-z]+)(\([a-z0-9_-]+\))?!?: (.+)$', header)
    if not match:
        errors.append(f"Header does not match '<type>(<scope>): <summary>' format: '{header}'")
    else:
        ctype = match.group(1)
        if ctype not in CONVENTIONAL_COMMIT_TYPES:
            errors.append(f"Unknown commit type '{ctype}'. Allowed: {', '.join(sorted(CONVENTIONAL_COMMIT_TYPES))}")
        summary = match.group(3)
        if summary.endswith("."):
            errors.append("Summary should not end with a period.")
        if len(header) > 72:
            errors.append(f"Header length ({len(header)}) exceeds 72 characters.")

    return len(errors) == 0, errors


def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return r, g, b


def _relative_luminance(r: float, g: float, b: float) -> float:
    def adjust(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r_adj = adjust(r)
    g_adj = adjust(g)
    b_adj = adjust(b)
    return 0.2126 * r_adj + 0.7152 * g_adj + 0.0722 * b_adj


def calculate_contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate WCAG 2.1 relative luminance contrast ratio between two hex colors."""
    r1, g1, b1 = _hex_to_rgb(hex1)
    r2, g2, b2 = _hex_to_rgb(hex2)
    l1 = _relative_luminance(r1, g1, b1)
    l2 = _relative_luminance(r2, g2, b2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def measure_hookscore(text: str) -> int:
    """Calculate a 0-100 retention hookscore for spoken vertical video scripts."""
    score = 50
    words = text.split()
    word_count = len(words)

    # 1. Brevity bonus: under 25 words in opening hook
    first_sentence = re.split(r'[.!?]', text.strip())[0].strip()
    first_sentence_words = len(first_sentence.split())

    if 5 <= first_sentence_words <= 18:
        score += 20
    elif first_sentence_words > 25:
        score -= 15

    # 2. Power hooks / pattern interruption
    power_keywords = ["stop", "how to", "never", "secret", "why you", "here is", "instead of", "3-step", "hack", "mistake"]
    lower_text = text.lower()
    for kw in power_keywords:
        if kw in lower_text:
            score += 5

    # 3. Slop penalties (passive, greeting, fluff)
    slop_phrases = ["hello everyone", "welcome back", "in this video", "today i want to", "dive deep", "game-changer", "tapestry"]
    for slop in slop_phrases:
        if slop in lower_text:
            score -= 20

    return max(0, min(100, score))
