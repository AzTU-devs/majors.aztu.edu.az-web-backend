from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    surname: str
    father_name: str
    email: EmailStr

class UpdateUser(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    father_name: Optional[str]
    email: Optional[EmailStr]