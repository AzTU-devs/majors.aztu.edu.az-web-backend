from app.db.session import get_db
from app.services.specialty import *
from app.utils.language import get_language
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.specialty import CreateSpecialty
from app.utils.jwt import token_required

router = APIRouter()

@router.get("/specialties")
async def get_specialities_endpoint(
    faculty_code: str = Query(None),
    cafedra_code: str = Query(None),
    specialty_name: str = Query(None),
    specialty_code: str = Query(None),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_specialties(
        faculty_code,
        cafedra_code,
        specialty_name,
        specialty_code,
        lang_code,
        db
    )

@router.get("/specialty/{specialty_code}")
async def get_specialty_details(
    specialty_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_specialty_by_specialty_code(specialty_code, lang_code, db)

@router.post("/specialty", dependencies=[Depends(token_required())])
async def create_specialty_endpoint(
    specialty_details: CreateSpecialty,
    db: AsyncSession = Depends(get_db)
):
    return await add_specialty(specialty_details, db)

@router.delete("/specialty/{specialty_code}", dependencies=[Depends(token_required())])
async def delete_specialty_endpoint(
    specialty_code: str,
    db: AsyncSession = Depends(get_db),
):
    return await delete_specialty(specialty_code, db)

@router.get("/specialties/{cafedra_code}")
async def get_specialties_by_cafedra_endpoint(
    cafedra_code: str,
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=0),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_specialties_by_cafedra(
        cafedra_code,
        start,
        end,
        lang_code,
        db
    )