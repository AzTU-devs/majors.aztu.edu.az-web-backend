from pydantic import BaseModel

class CreateTlo(BaseModel):
    topic_code: str
    tlo_content: str

class UpdateTlo(BaseModel):
    tlo_code: str
    tlo_content: str