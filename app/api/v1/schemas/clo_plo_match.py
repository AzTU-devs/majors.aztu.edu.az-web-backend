from pydantic import BaseModel


class CloPloMatchPayload(BaseModel):
    clo_code: str
    plo_code: str
    match: bool = True
