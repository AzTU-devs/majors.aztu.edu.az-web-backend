from typing import List, Optional
from pydantic import BaseModel


class CreateGeneralSubject(BaseModel):
    owner_cafedra_code: str
    # Specialties (from other cafedras) this general subject is assigned to.
    specialty_codes: List[str]
    subject_code: str
    subject_name: str
    subject_desc: str
    semester: int
    status: int
    credit: int
    year: str
    hours_per_week: int
    form_of_education: Optional[int] = None
    language_of_instruction: Optional[int] = None
    in_class_hours: Optional[str] = None
    out_of_class_hours: Optional[str] = None
    teaching_methods: Optional[str] = None
    assessment: Optional[str] = None
