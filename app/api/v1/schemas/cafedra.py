from pydantic import BaseModel

class CafedraBase(BaseModel):
    university_code: str
    faculty_code: str
    cafedra_code: str
    cafera_name: str

class CreateCafedra(BaseModel):
    university_code: str

class CreateCafedraManual(BaseModel):
    faculty_code: str
    cafedra_code: str
    cafedra_name: str