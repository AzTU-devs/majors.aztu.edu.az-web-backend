from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.schemas.gco import GCOCreate, GCOUpdate
from app.utils.language import get_language
from app.services import gco as gco_service
from app.utils.jwt import token_required

router = APIRouter()

# GET All GCOs
@router.get("/gco-all")
async def get_all_gcos(lang: str = Depends(get_language), db: AsyncSession = Depends(get_db)):
    return await gco_service.get_all_gcos(db=db, lang=lang)


# GET by specialty code
@router.get("/gco/{specialty_code}")
async def get_gcos_by_specialty(specialty_code: str, lang: str = Depends(get_language), db: AsyncSession = Depends(get_db)):
    return await gco_service.get_gcos_by_specialty(specialty_code=specialty_code, lang=lang, db=db)


# POST Create new GCO
@router.post("/gco", dependencies=[Depends(token_required())])
async def create_gco(gco_data: GCOCreate, db: AsyncSession = Depends(get_db)):
    return await gco_service.create_gco(db=db, gco_data=gco_data)

# PUT Update GCO
@router.put("/gco/{career_code}", dependencies=[Depends(token_required())])
async def update_gco(career_code: str, gco_data: GCOUpdate, db:AsyncSession = Depends(get_db)):
    return await gco_service.update_gco(db=db, career_code=career_code, gco_data=gco_data)

# DELETE GCO
@router.delete("/gco/{career_code}", dependencies=[Depends(token_required())])
async def delete_gco(career_code: str, db: AsyncSession = Depends(get_db)):
    return await gco_service.delete_gco(db=db, career_code=career_code)