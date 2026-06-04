from typing import Optional
from pydantic import BaseModel

class CompetencyTranslationCreate(BaseModel):
    language_code: str
    competency_content: str

class CompetencyCreate(BaseModel):
    specialty_code: str
    competency_content: str
    # 1 = Peşə (Job), 2 = İxtisas (Specialty)
    competency_type: int = 2

class CompetencyUpdate(BaseModel):
    competency_content: str
    competency_type: Optional[int] = None

class CompetencyTranslationOut(BaseModel):
    language_code: str
    competency_content: str
