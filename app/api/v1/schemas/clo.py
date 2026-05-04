from pydantic import BaseModel

class CreateClo(BaseModel):
    subject_code: str
    clo_content: str