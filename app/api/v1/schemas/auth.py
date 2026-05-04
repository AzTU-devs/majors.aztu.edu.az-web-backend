from pydantic import BaseModel

class AuthBase(BaseModel):
    name: str
    surname: str
    father_name: str
    fin_kod: str
    cafedra_code: str

class SignUp(AuthBase):
    password: str
    email: str
    pass

class SignIn(BaseModel):
    fin_kod: str
    password: str

class ValidateOTP(BaseModel):
    fin_kod: str
    otp: int