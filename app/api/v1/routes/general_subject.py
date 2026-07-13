from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.utils.jwt import token_required
from app.utils.language import get_language
from app.api.v1.schemas.general_subject import CreateGeneralSubject
from app.services.general_subject import (
    create_general_subject,
    get_general_subjects_by_cafedra,
    delete_general_subject,
)

router = APIRouter()


@router.post("/general-subjects", dependencies=[Depends(token_required())])
async def create_general_subject_endpoint(
    payload: CreateGeneralSubject,
    db: AsyncSession = Depends(get_db),
):
    return await create_general_subject(payload, db)


@router.get("/general-subjects/{cafedra_code}")
async def list_general_subjects_endpoint(
    cafedra_code: str = Path(...),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
):
    return await get_general_subjects_by_cafedra(cafedra_code, lang_code, db)


@router.delete("/general-subjects/{subject_code}", dependencies=[Depends(token_required())])
async def delete_general_subject_endpoint(
    subject_code: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    return await delete_general_subject(subject_code, db)
