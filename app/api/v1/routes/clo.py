from app.services.clo import *
from app.db.session import get_db
from fastapi import APIRouter, Depends
from app.utils.language import get_language
from app.api.v1.schemas.clo import CreateClo, UpdateClo
from app.utils.jwt import token_required
from fastapi import Path
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/clo/create", dependencies=[Depends(token_required())])
async def create_clo_endpoint(
    clo_request: CreateClo,
    db: AsyncSession = Depends(get_db)
):
    return await add_clo(clo_request, db)

@router.put("/clo/{clo_code}", dependencies=[Depends(token_required())])
async def update_clo_endpoint(
    clo_request: UpdateClo,
    clo_code: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    return await update_clo(clo_code, clo_request, db)

@router.get("/clo/{subject_code}")
async def get_clo_endpoint(
    subject_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_clo_by_subject_code(subject_code, lang_code, db)