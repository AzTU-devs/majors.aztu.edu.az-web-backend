from pydantic import BaseModel


class MatchPayload(BaseModel):
    subject_code: str
    plo_code: str
    match: bool = True
