from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.utils.language import get_language
from app.api.v1.schemas.literature import CreateLiterature, UpdateLiterature
from app.services.literature import LiteratureCRUD
from app.utils.jwt import token_required
from typing import Optional

router = APIRouter()
literature_crud = LiteratureCRUD()

@router.post("/create", dependencies=[Depends(token_required())])
async def create_literature(
    literature: CreateLiterature,
    db: AsyncSession = Depends(get_db)
):
    """Yeni literature yaradır (fənnə bağlı)"""
    return await literature_crud.add_literature(literature, db)

@router.get("/subject/{subject_code}")
async def get_literatures_by_subject(
    subject_code: str,
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=1),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    """Fənn koduna görə ədəbiyyatları gətirir"""
    return await literature_crud.get_literature_by_subject_code(
        subject_code, start, end, lang_code, db
    )

@router.get("/specialty/{specialty_code}")
async def get_literatures_by_specialty(
    specialty_code: int,
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=1),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    """Specialty code-a görə literature-ləri gətirir (köhnə)"""
    return await literature_crud.get_literature_by_specialty_code(
        specialty_code, start, end, lang_code, db
    )

@router.get("/code/{literature_code}")
async def get_literature_by_code(
    literature_code: int,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    """Literature code-a görə literature gətirir"""
    return await literature_crud.get_literature_by_code(literature_code, lang_code, db)

@router.get("/")
async def get_all_literatures(
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=1),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    """Bütün literature-ləri gətirir"""
    return await literature_crud.get_all_literatures(start, end, lang_code, db)

@router.put("/{literature_code}", dependencies=[Depends(token_required())])
async def update_literature(
    literature_code: int,
    literature: UpdateLiterature,
    db: AsyncSession = Depends(get_db)
):
    """Literature yeniləyir"""
    return await literature_crud.update_literature(literature_code, literature, db)

@router.delete("/{literature_code}", dependencies=[Depends(token_required())])
async def delete_literature(
    literature_code: int,
    db: AsyncSession = Depends(get_db)
):
    """Literature silir"""
    return await literature_crud.delete_literature(literature_code, db)

@router.get("/search/")
async def search_literatures(
    search_term: str = Query(..., description="Axtarış termini"),
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=1),
    specialty_code: Optional[int] = Query(None),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    """Literature axtarışı"""
    return await literature_crud.search_literatures(
        search_term, start, end, lang_code, specialty_code, db
    )