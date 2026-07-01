from app.db.session import get_db
from app.services.cafedra import *
from app.utils.jwt import token_required
from app.utils.language import get_language
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.cafedra import CreateCafedraManual, UpdateCafedraManual

router = APIRouter()

@router.post("/lms/cafedras", dependencies=[Depends(token_required())])
async def lms_cafedras_endpoint(
    db: AsyncSession = Depends(get_db)
):
    return await get_cafedras_from_lms(db)

@router.post("/cafedra")
async def create_cafedra_endpoint(
    payload: CreateCafedraManual,
    db: AsyncSession = Depends(get_db),
):
    return await add_cafedra_manual(payload, db)

@router.put("/cafedra/{cafedra_code}")
async def update_cafedra_endpoint(
    payload: UpdateCafedraManual,
    cafedra_code: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    return await update_cafedra_manual(cafedra_code, payload, db)

@router.delete("/cafedra/{cafedra_code}")
async def delete_cafedra_endpoint(
    cafedra_code: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    return await delete_cafedra_manual(cafedra_code, db)

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