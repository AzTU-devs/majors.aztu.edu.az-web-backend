from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.schemas.competency import CompetencyCreate, CompetencyUpdate
from app.utils.language import get_language
from app.services import competency as competency_service
from app.utils.jwt import token_required

router = APIRouter()

# GET All Competencies
@router.get("/competency-all")
async def get_all_competency(lang: str = Depends(get_language), db: AsyncSession = Depends(get_db)):
    return await competency_service.get_all_competency(db=db, lang=lang)


# GET by specialty code (optionally filtered by competency type: 1=Job, 2=Specialty)
@router.get("/competency/{specialty_code}")
async def get_competencies_by_specialty(
    specialty_code: str,
    lang: str = Depends(get_language),
    type: Optional[int] = Query(default=None, description="1=Job (Peşə), 2=Specialty (İxtisas)"),
    db: AsyncSession = Depends(get_db),
):
    return await competency_service.get_competencies_by_specialty(
        specialty_code=specialty_code, lang=lang, db=db, competency_type=type
    )

# POST Create new Competency
@router.post("/competency", dependencies=[Depends(token_required())])
async def create_competency(competency_data: CompetencyCreate, db: AsyncSession = Depends(get_db)):
    return await competency_service.create_competency(db=db, competency_data=competency_data)

# PUT Update Competency
@router.put("/competency/{competency_code}", dependencies=[Depends(token_required())])
async def update_competency(competency_code: str, competency_data: CompetencyUpdate, db:AsyncSession = Depends(get_db)):
    return await competency_service.update_competency(db=db, competency_code=competency_code, competency_data=competency_data)

# DELETE Competency
@router.delete("/competency/{competency_code}", dependencies=[Depends(token_required())])
async def delete_competency(competency_code: str, db: AsyncSession = Depends(get_db)):
    return await competency_service.delete_competency(db=db, competency_code=competency_code)