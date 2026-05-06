from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.plo import get_plos_by_specialty, create_plo as create_plo_service, delete_plo, update_plo, get_all_plos as get_all_plos_service
from app.api.v1.schemas.plo import PloCreate, PloUpdate
from app.utils.language import get_language
from app.services import plo as plo_service
from app.utils.jwt import token_required

router  = APIRouter()

# GET all PLOs
@router.get("/plo-all", response_model=None)
async def get_all_plos(db: AsyncSession = Depends(get_db), lang: str = Depends(get_language)):
    return await get_all_plos_service(db, lang)

# GET PLO by specialty_code
@router.get("/plo/{specialty_code}", response_model=None)
async def get_plos(specialty_code: str, lang: str = Depends(get_language), db: AsyncSession = Depends(get_db)):
    return await plo_service.get_plos_by_specialty(specialty_code, lang, db)

# POST create new PLO
@router.post("/plo", response_model=None, dependencies=[Depends(token_required())])
async def create_plo(plo_data: PloCreate, db: AsyncSession = Depends(get_db)):
    return await plo_service.create_plo(db, plo_data)

# DELETE PLO by plo_code
@router.delete("/plo/{plo_code}", dependencies=[Depends(token_required())])
async def delete_plo_endpoint(plo_code: str, db: AsyncSession = Depends(get_db)):
    return await plo_service.delete_plo(db, plo_code)

# UPDATE by plo_code
@router.put("/plo/{plo_code}", response_model=None, dependencies=[Depends(token_required())])
async def update_plo_endpoint(
    plo_code: str,
    plo_data: PloUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await plo_service.update_plo(db, plo_code, plo_data)











