from passlib.context import CryptContext

pwd_content = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_pass: str) -> str:
    return pwd_content.hash(plain_pass)

def verify_password(plain_pass: str, hashed_pass) -> str:
    return pwd_content.verify(
        plain_pass, hashed_pass
    )