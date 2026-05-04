from typing import Dict
from pydantic import BaseModel

class CreateCurricula(BaseModel):
    subject_code: str
    specialty_code: str
    subject_name: str
    subject_desc: str
    semester: int
    status: int
    credit: int
    year: int
    hours_per_week: int

class UpdateCurricula(BaseModel):
    semester: int = None
    status: str = None
    year: int = None
    credit: int = None
    hours_per_week: int = None
    subject_name: Dict[str, str] = None
    subject_description: Dict[str, str] = None