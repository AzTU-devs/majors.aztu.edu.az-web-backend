from pydantic import BaseModel

class SpecialtyCharacteristicsTranslationCreate(BaseModel):
    language_code: str  
    program_desc: str
    degree_requirements: str

class SpecialtyCharacteristicsCreate(BaseModel):
    specialty_code: str
    program_desc: str
    degree_requirements: str

class SpecialtyCharacteristicsUpdate(BaseModel):
    program_desc: str
    degree_requirements: str

class SpecialtyCharacteristicsTranslationOut(BaseModel):
    language_code: str
    program_desc: str
    degree_requirements: str