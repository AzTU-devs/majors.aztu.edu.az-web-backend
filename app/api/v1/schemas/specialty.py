from pydantic import BaseModel

class SpecialtyBase(BaseModel):
    cafedra_code: str
    specialty_code: str
    specialty_name: str

class CreateSpecialty(SpecialtyBase):
    pass