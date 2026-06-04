from typing import Optional
from pydantic import BaseModel

class CreateTopic(BaseModel):
    subject_code: str
    topic_name: str
    topic_desc: str
    topic_result: str
    topic_url: str
    topic_type: int

class UpdateTopic(BaseModel):
    topic_code: str
    topic_name: Optional[str] = None
    topic_desc: Optional[str] = None
    topic_result: Optional[str] = None
    topic_url: Optional[str] = None
    topic_type: Optional[int] = None