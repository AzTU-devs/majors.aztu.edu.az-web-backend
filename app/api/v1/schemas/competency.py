from pydantic import BaseModel

class CompetencyTranslationCreate(BaseModel):
    language_code: str
    competency_content: str

class CompetencyCreate(BaseModel):
    specialty_code: str
    competency_content: str

class CompetencyUpdate(BaseModel):
    competency_content: str

class CompetencyTranslationOut(BaseModel):
    language_code: str
    competency_content: str
