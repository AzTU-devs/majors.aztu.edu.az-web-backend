from pydantic import BaseModel
from typing import List

class SloTranslationCreate(BaseModel):
    language_code: str
    slo_content: str

class SloCreate(BaseModel):
    specialty_code: str
    slo_content: str

class SloUpdate(BaseModel):
    slo_content: str

class SloTranslationOut(BaseModel):
    language_code: str
    slo_content: str

class SloOut(BaseModel):
    id: int
    specialty_code: str
    slo_code: str
    translations: List[SloTranslationOut]