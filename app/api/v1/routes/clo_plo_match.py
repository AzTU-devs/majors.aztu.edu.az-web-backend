from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.utils.jwt import token_required
from app.api.v1.schemas.clo_plo_match import CloPloMatchPayload
from app.services.clo_plo_match import (
    toggle_clo_plo_match,
    get_clo_plo_matches_by_subject,
    get_clo_plo_matches_by_clo,
)

router = APIRouter()


@router.post("/clo-plo-match", dependencies=[Depends(token_required())])
async def create_clo_plo_match_endpoint(
    payload: CloPloMatchPayload,
    db: AsyncSession = Depends(get_db),
):
    return await toggle_clo_plo_match(payload, db)


@router.get("/clo-plo-match/subject/{subject_code}")
async def clo_plo_matches_by_subject_endpoint(
    subject_code: str,
    db: AsyncSession = Depends(get_db),
):
    return await get_clo_plo_matches_by_subject(subject_code, db)


@router.get("/clo-plo-match/clo/{clo_code}")
async def clo_plo_matches_by_clo_endpoint(
    clo_code: str,
    db: AsyncSession = Depends(get_db),
):
    return await get_clo_plo_matches_by_clo(clo_code, db)
