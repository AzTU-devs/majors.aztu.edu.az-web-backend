import random

async def generateOtp(length: int = 6) -> str:
    otp = ''.join(str(random.randint(0, 9)) for _ in range(length))
    return otp