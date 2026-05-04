from app.services.auth import *
from app.db.session import get_db
from fastapi import APIRouter, Depends
from app.api.v1.schemas.auth import SignUp
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()