from pydantic import BaseModel
from typing import List, Optional


class PloTranslationCreate(BaseModel):
    language_code: str
    plo_content: str

class PloCreate(BaseModel):
    specialty_code: str
    plo_content: str

class PloUpdate(BaseModel):
    plo_content: str

class PloTranslationOut(BaseModel):
    language_code: str
    plo_content: str

class PloOut(BaseModel):
    id: int
    specialty_code: str
    plo_code: str