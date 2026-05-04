from pydantic import BaseModel

class ValidateOtp(BaseModel):
    fin_kod: str
    otp: int