from typing import Optional
from pydantic import BaseModel


class CreateAdmin(BaseModel):
    name: str
    surname: str
    email: str
    fin_kod: str
    password: str


class UpdateAdmin(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    approved: Optional[bool] = None
