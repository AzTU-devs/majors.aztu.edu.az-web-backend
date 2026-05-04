from typing import List
from pydantic import BaseModel

class GCOTranslationCreate(BaseModel):
    language_code: str
    career_content: str

class GCOCreate(BaseModel):
    specialty_code: str
    career_title: str
    career_content: str

class GCOUpdate(BaseModel):
    career_content: str

class GCOTranslationOut(BaseModel):
    language_code: str
    career_content: str

class GCOOut(BaseModel):
    id: int
    specialty_code: str
    career_code: str
    translations: List[GCOTranslationOut]