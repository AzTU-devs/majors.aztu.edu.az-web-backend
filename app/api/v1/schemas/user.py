from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    surname: str
    father_name: str
    email: str

class UpdateUser(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    father_name: Optional[str] = None
    email: Optional[str] = None

class ApproveUser(BaseModel):
    fin_kod: str
    approved: bool = True