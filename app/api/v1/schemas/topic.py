from pydantic import BaseModel

class CreateTopic(BaseModel):
    subject_code: str
    topic_name: str
    topic_desc: str
    topic_result: str
    topic_url: str
    topic_type: int