from app.services.tlo import *
from app.db.session import get_db
from fastapi import APIRouter, Depends
from app.utils.language import get_language
from app.api.v1.schemas.tlo import CreateTlo, UpdateTlo
from app.utils.jwt import token_required
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/tlo/create", dependencies=[Depends(token_required())])
async def create_tlo_endpoint(
    tlo_request: CreateTlo,
    db: AsyncSession = Depends(get_db)
):
    return await add_tlo(tlo_request, db)

@router.patch("/tlo/update", dependencies=[Depends(token_required())])
async def update_tlo_endpoint(
    tlo_request: UpdateTlo,
    db: AsyncSession = Depends(get_db)
):
    return await update_tlo(tlo_request, db)

@router.delete("/tlo/{tlo_code}", dependencies=[Depends(token_required())])
async def delete_tlo_endpoint(
    tlo_code: str,
    db: AsyncSession = Depends(get_db)
):
    return await delete_tlo(tlo_code, db)

@router.get("/tlo/topic/{topic_code}")
async def get_tlo_by_topic_endpoint(
    topic_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_tlo_by_topic_code(topic_code, lang_code, db)
