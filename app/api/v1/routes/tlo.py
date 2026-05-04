from app.services.tlo import *
from app.db.session import get_db
from fastapi import APIRouter, Depends
from app.utils.language import get_language
from app.api.v1.schemas.tlo import CreateTlo
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/tlo/create")
async def create_tlo_endpoint(
    clo_request: CreateTlo,
    db: AsyncSession = Depends(get_db)
):
    return await add_tlo(clo_request, db)

@router.get("/tlo/{subject_code}")
async def get_tlo_endpoint(
    subject_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_tlo_by_subject_code(subject_code, lang_code, db)