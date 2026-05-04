from app.db.session import get_db
from app.services.cafedra import *
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/lms/cafedras")
async def lms_cafedras_endpoint(
    db: AsyncSession = Depends(get_db)
):
    return await get_cafedras_from_lms(db)

@router.get("/cafedras")
async def list_cafedras(
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_cafedras(lang_code, db)

@router.get("/cafedras/{faculty_code}")
async def get_cafedras_by_fac_code_endpoint(
    faculty_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_cafedra_by_faculty(faculty_code, lang_code, db)