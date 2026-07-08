"""Shared validation for entity codes (subject, specialty, faculty, cafedra).

Codes must use a single consistent structure across the whole platform:
letters, digits, and only the symbols ``(``, ``)`` and ``-``. Spaces and any
other symbol are rejected, so a code can never break a URL lookup (which caused
subjects to list fine but 404 on open).
"""

_ALLOWED_SYMBOLS = set("()-")


def is_valid_code(code: str) -> bool:
    """True if ``code`` is non-empty and only letters/digits/()- (no spaces)."""
    if not code:
        return False
    for ch in code:
        if ch.isalnum() or ch in _ALLOWED_SYMBOLS:
            continue
        return False
    return True


CODE_RULE_MESSAGE = (
    "Invalid code. Use only letters, digits and the symbols ( ) - "
    "(no spaces or other characters)."
)
