from pydantic import BaseModel

class CreateTlo(BaseModel):
    subject_code: str
    tlo_content: str