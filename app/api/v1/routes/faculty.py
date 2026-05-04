from app.db.session import get_db
from app.services.faculty import *
from app.utils.language import get_language
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/lms/faculties")
async def lms_faculties(
    db: AsyncSession = Depends(get_db)
):
    return await get_faculties_from_lms(db)

@router.get("/faculties")
async def get_faculties_endpoint(
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_faculties(lang_code, db)

@router.get("/faculties/{uni_code}")
async def get_uni_faculties_endpoint(
    db: AsyncSession = Depends(get_db)
):
    return await get_faculties(db)