from pydantic import BaseModel

class CreateClo(BaseModel):
    subject_code: str
    clo_content: str

class UpdateClo(BaseModel):
    clo_content: str