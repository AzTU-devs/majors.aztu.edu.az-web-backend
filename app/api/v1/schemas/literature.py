from pydantic import BaseModel
from typing import Optional

class CreateLiterature(BaseModel):
    subject_code: str
    url: str
    literature_name: str

class UpdateLiterature(BaseModel):
    subject_code: Optional[str] = None
    url: Optional[str] = None
    literature_name: Optional[str] = None