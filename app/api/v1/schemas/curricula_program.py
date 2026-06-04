from typing import Dict, Optional
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
    form_of_education: Optional[int] = None
    language_of_instruction: Optional[int] = None
    in_class_hours: Optional[str] = None
    teaching_methods: Optional[str] = None
    assessment: Optional[str] = None

class UpdateCurricula(BaseModel):
    semester: Optional[int] = None
    status: Optional[int] = None
    year: Optional[int] = None
    credit: Optional[int] = None
    hours_per_week: Optional[int] = None
    form_of_education: Optional[int] = None
    language_of_instruction: Optional[int] = None
    in_class_hours: Optional[str] = None
    teaching_methods: Optional[str] = None
    assessment: Optional[str] = None
    subject_name: Optional[Dict[str, str]] = None
    subject_description: Optional[Dict[str, str]] = None
