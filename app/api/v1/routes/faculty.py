from app.db.session import get_db
from app.services.faculty import *
from app.utils.language import get_language
from app.utils.jwt import token_required
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.faculty import CreateFacultyManual

router = APIRouter()

@router.post("/lms/faculties", dependencies=[Depends(token_required())])
async def lms_faculties(
    db: AsyncSession = Depends(get_db)
):
    return await get_faculties_from_lms(db)

@router.post("/faculty")
async def create_faculty_endpoint(
    payload: CreateFacultyManual,
    db: AsyncSession = Depends(get_db),
):
    return await add_faculty_manual(payload, db)

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