from app.db.session import get_db
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.university import CreateUniversity
from app.services.university import get_universities, get_university, add_university, delete_university
from app.utils.jwt import token_required

router = APIRouter()

@router.get("/universities")
async def get_unis_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_universities(db)

@router.get("/university")
async def get_university_endpoint(
    university_code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    return await get_university(university_code, db)

@router.post("/university", dependencies=[Depends(token_required())])
async def create_university_endpoint(
    university_details: CreateUniversity,
    db: AsyncSession = Depends(get_db)
):
    return await add_university(university_details, db)

@router.delete("/university", dependencies=[Depends(token_required())])
async def delete_university_endpoint(
    university_code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    return await delete_university(university_code, db)