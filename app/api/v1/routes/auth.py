from app.services.auth import *
from app.db.session import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.auth import SignUp, SignIn

router = APIRouter()

@router.post("/signup")
async def signup_endpoint(
    user: SignUp,
    db: AsyncSession = Depends(get_db)
):
    return await signup(user, db)

@router.post("/signin")
async def signin_endpoint(
    credentials: SignIn,
    db: AsyncSession = Depends(get_db)
):
    return await signin(credentials, db)