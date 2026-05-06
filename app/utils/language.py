from fastapi import Query
from typing import Optional, Annotated

DEFAULT_LANGUAGE = "az"
ALLOWED_LANGUAGES = {"en", "az"}


async def get_language(
    lang: Annotated[Optional[str], Query(description="Language code: 'az' or 'en'")] = None,
) -> str:
    if lang and lang.strip():
        candidate = lang.strip().lower()
        if candidate in ALLOWED_LANGUAGES:
            return candidate
    return DEFAULT_LANGUAGE
