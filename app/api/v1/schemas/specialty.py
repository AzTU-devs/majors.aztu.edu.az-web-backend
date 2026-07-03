from typing import Optional
from pydantic import BaseModel

class SpecialtyBase(BaseModel):
    cafedra_code: str
    specialty_code: str
    specialty_name: str

class CreateSpecialty(SpecialtyBase):
    pass

class UpdateSpecialty(BaseModel):
    specialty_name: Optional[str] = None
    new_specialty_code: Optional[str] = None