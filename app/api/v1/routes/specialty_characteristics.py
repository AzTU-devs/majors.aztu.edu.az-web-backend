from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.schemas.specialty_characteristics import ( 
    SpecialtyCharacteristicsCreate,
    SpecialtyCharacteristicsUpdate
)
from app.utils.language import get_language
from app.services import specialty_characteristics as specialty_service

router = APIRouter()

# GET All Specialty Characteristics
@router.get("/specialty-characteristics-all")
async def get_all_specialty_characteristics(lang: str = Depends(get_language),db: AsyncSession = Depends(get_db)):
    return await specialty_service.get_all_specialty_characteristics(db=db, lang=lang)


# GET by specialty_code
@router.get("/specialty-characteristics/{specialty_code}")
async def get_specialty_characteristics_by_specialty(specialty_code: str, lang: str = Depends(get_language), db: AsyncSession = Depends(get_db)):
    return await specialty_service.get_specialty_characteristics_by_specialty(specialty_code=specialty_code, lang=lang, db=db)


# POST Create new Specialty Characteristic
@router.post("/specialty-characteristics")
async def create_specialty_characteristic(specialty_data: SpecialtyCharacteristicsCreate, db: AsyncSession = Depends(get_db)):
    return await specialty_service.create_specialty_characteristics(db=db, char_data=specialty_data)


# PUT Update Specialty Characteristic
@router.put("/specialty-characteristics/{specialty_code}")
async def update_specialty_characteristic(specialty_code: str, specialty_data: SpecialtyCharacteristicsUpdate, db: AsyncSession = Depends(get_db)):
    return await specialty_service.update_specialty_characteristics(db=db, specialty_code=specialty_code, char_data=specialty_data)


# DELETE Specialty Characteristic
@router.delete("/specialty-characteristics/{specialty_code}")
async def delete_specialty_characteristic(specialty_code: str, db: AsyncSession = Depends(get_db)):
    return await specialty_service.delete_specialty_characteristics(db=db, specialty_code=specialty_code)