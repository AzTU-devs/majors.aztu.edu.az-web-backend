from pydantic import BaseModel
from typing import Optional

class CreateLiterature(BaseModel):
    literature_code: int
    specialty_code: int
    url: str
    literature_name: str

class UpdateLiterature(BaseModel):
    specialty_code: Optional[int] = None
    url: Optional[str] = None
    literature_name: Optional[str] = None