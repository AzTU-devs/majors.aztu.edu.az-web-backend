from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.utils.jwt import token_required
from app.api.v1.schemas.match import MatchPayload
from app.services.match import toggle_match, get_matches_by_subject

router = APIRouter()


@router.post("/match", dependencies=[Depends(token_required())])
async def create_match_endpoint(
    payload: MatchPayload,
    db: AsyncSession = Depends(get_db),
):
    return await toggle_match(payload, db)


@router.get("/match/subject/{subject_code}")
async def matches_by_subject_endpoint(
    subject_code: str,
    db: AsyncSession = Depends(get_db),
):
    return await get_matches_by_subject(subject_code, db)
