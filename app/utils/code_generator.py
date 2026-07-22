"""Collision-resistant generator for internal entity codes.

Entity codes (topic, tlo, plo, clo, ...) are the *only* link between a row and
its translations and children — there are no foreign keys, the join is on the
code string. The original generators used ``random.randint(10000, 99999)`` with
no uniqueness check and no unique index, a 90,000-value space that by the
birthday bound collides with ~50% probability at only ~350 rows.

A collision silently merges two unrelated records: the translation lookup does
``.first()``, so one entity renders the other's text, and a delete removes both
entities' translations. This produced topics from one cafedra's subject showing
up in another's.

Codes generated here are opaque identifiers — never parsed, never shown to a
user, only passed back as URL/API parameters — so the wider format is safe.
"""

import uuid


def generate_code(prefix: str) -> str:
    """Return a unique code like ``TOPIC-3f9a1c04b7e2``.

    48 bits of randomness: collision probability stays negligible well past any
    row count this platform will reach.
    """
    return f"{prefix}-{uuid.uuid4().hex[:12]}"
