from pydantic import BaseModel

class UniversityBase(BaseModel):
    university_name: str
    university_short_name: str

class CreateUniversity(UniversityBase):
    pass