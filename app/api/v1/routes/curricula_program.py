from app.db.session import get_db
from app.utils.language import get_language
from app.services.curricula_program import *
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.curricula_program import *

router = APIRouter()

@router.post("/curricula/create")
async def create_curricula_endpoint(
    curricula_req: CreateCurricula,
    db: AsyncSession = Depends(get_db)
):
    return await add_curricula(curricula_req, db)

@router.get("/curricula/{specialty_code}/subjects")
async def get_subjects_endpoint(
    specialty_code: str,
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=0),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_curricula_by_specialty(specialty_code, start, end, lang_code, db)

@router.get("/curricula/{subject_code}")
async def get_subject_details_endpoint(
    subject_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_curricula_by_subject(subject_code, lang_code, db)

@router.delete("/curricula/{subject_code}/delete")
async def deleet_curricula_endpoint(
    subject_code: str,
    db: AsyncSession = Depends(get_db)
):
    return await delete_curricula(subject_code, db)

@router.patch("/curricula/{subject_code}/update")
async def update_curricula_endpoint(
    subject_code: str,
    update_data: UpdateCurricula,
    db: AsyncSession = Depends(get_db)
):
    return await update_curricula(subject_code, update_data, db)