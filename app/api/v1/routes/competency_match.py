from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.utils.jwt import token_required
from app.api.v1.schemas.competency_match import CompetencyMatchPayload
from app.services.competency_match import (
    toggle_competency_match,
    get_matches_by_competency,
    get_matches_by_subject,
)

router = APIRouter()


@router.post("/competency-match", dependencies=[Depends(token_required())])
async def create_competency_match_endpoint(
    payload: CompetencyMatchPayload,
    db: AsyncSession = Depends(get_db),
):
    return await toggle_competency_match(payload, db)


@router.get("/competency-match/competency/{competency_code}")
async def matches_by_competency_endpoint(
    competency_code: str,
    db: AsyncSession = Depends(get_db),
):
    return await get_matches_by_competency(competency_code, db)


@router.get("/competency-match/subject/{subject_code}")
async def matches_by_subject_endpoint(
    subject_code: str,
    db: AsyncSession = Depends(get_db),
):
    return await get_matches_by_subject(subject_code, db)
