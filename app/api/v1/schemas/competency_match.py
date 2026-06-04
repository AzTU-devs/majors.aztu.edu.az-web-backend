from pydantic import BaseModel


class CompetencyMatchPayload(BaseModel):
    subject_code: str
    competency_code: str
    match: bool = True
