from pydantic import BaseModel

class FacultyBase(BaseModel):
    university_code: str
    faculty_code: str
    faculty_name: str

class CreateFaculty(BaseModel):
    university_code: str