from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from typing import List
from app.api.v1.schemas.slo import SloCreate, SloOut, SloTranslationOut, SloUpdate
from app.services import slo as slo_service
from app.utils.language import get_language
from app.services.slo import get_all_slos as get_all_slos_service

router = APIRouter()

# GET all SLOs
@router.get("/slo-all", response_model=None)
async def get_all_slos(db: AsyncSession = Depends(get_db), lang: str = Depends(get_language)):
    return await get_all_slos_service(db, lang)

# GET SLO by specialty_code
@router.get("/slo/{specialty_code}", response_model=None)
async def get_slos(specialty_code: str, lang: str = Depends(get_language), db: AsyncSession = Depends(get_db)):
    return await slo_service.get_slos_by_specialty(specialty_code, lang, db)

# POST create new SLO
@router.post("/slo", response_model=None)
async def create_slo(slo_data: SloCreate, db: AsyncSession = Depends(get_db)):
    return await slo_service.create_slo(db, slo_data)

# DELETE SLO by slo_code
@router.delete("/slo/{slo_code}")
async def delete_slo_endpoint(slo_code: str, db: AsyncSession = Depends(get_db)):
    return await slo_service.delete_slo(db, slo_code)

# UPDATE by slo_code
@router.put("/slo/{slo_code}", response_model=None)
async def update_slo_endpoint(
    slo_code: str,
    slo_data: SloUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await slo_service.update_slo(db, slo_code, slo_data)