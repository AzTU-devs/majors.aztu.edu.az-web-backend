from fastapi import status, Query, Header, HTTPException
from typing import Optional, Annotated

DEFAULT_LANGUAGE = "az"
ALLOWED_LANGUAGES = {"en", "az"}

async def get_language(
    lang: Annotated[Optional[str], Query(description="Query param to override language")] = None,
    accept_language: Annotated[Optional[str], Header(description="Accept-Language header")] = None
) -> str:
    
    language = DEFAULT_LANGUAGE

    if lang and lang.strip():
        language = lang.strip().lower()
    
    elif accept_language:
        primary_lang = accept_language.split(",")[0].split("-")[0].strip().lower()
        if primary_lang:
            language = primary_lang

    if language not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid language code '{language}'. Allowed values: {', '.join(ALLOWED_LANGUAGES)}"
        )

    return language