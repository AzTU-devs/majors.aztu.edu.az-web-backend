import random
from datetime import datetime
from app.models.clo import Clo
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.api.v1.schemas.clo import CreateClo
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translation.clo_translations import CloTranslations
from app.models.curricula_program import CurriculaProgram

def generate_clo_code():
    random_number = random.randint(10000, 99999)
    return f"CLO-{random_number}"

async def add_clo(
    clo_request: CreateClo,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        subject_query = await db.execute(
            select(CurriculaProgram)
            .where(CurriculaProgram.subject_code == clo_request.subject_code)
        )

        subject = subject_query.scalars().first()

        if not subject:
            return JSONResponse(
                content={
                   "status_code": 404,
                   "message": "Subject not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        clo_code = generate_clo_code()
        
        new_clo = Clo(
            subject_code=clo_request.subject_code,
            clo_code=clo_code,
            created_at=datetime.utcnow()
        )

        new_clo_az = CloTranslations(
            clo_code=clo_code,
            language_code="az",
            clo_content=clo_request.clo_content,
            created_at=datetime.utcnow()
        )

        new_clo_en = CloTranslations(
            clo_code=clo_code,
            language_code="en",
            clo_content=translate_to_english(clo_request.clo_content),
            created_at=datetime.utcnow()
        )

        db.add(new_clo)
        db.add(new_clo_az)
        db.add(new_clo_en)
        await db.commit()
        await db.refresh(new_clo)
        await db.refresh(new_clo_az)
        await db.refresh(new_clo_en)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Clo added successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_clo_by_subject_code(
    subject_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        subject_query = await db.execute(
            select(CurriculaProgram)
            .where(CurriculaProgram.subject_code == subject_code)
        )

        subject = subject_query.scalars().first()

        if not subject:
            return JSONResponse(
                content={
                   "status_code": 404,
                   "message": "Subject not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        clo_query = await db.execute(
            select(Clo)
            .where(Clo.subject_code == subject_code)
        )

        clos = clo_query.scalars().all()

        if not clos:
            return JSONResponse(
                content={
                   "status_code": 204,
                   "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        clos_arr = []

        for clo in clos:
            clo_content_query = await db.execute(
                select(CloTranslations)
                .where(
                    CloTranslations.clo_code == clo.clo_code,
                    CloTranslations.language_code == lang_code
                )
            )

            clo_content = clo_content_query.scalar_one_or_none().clo_content

            clo_obj = {
                "subject_code": subject_code,
                "clo_code": clo.clo_code,
                "clo_type": clo.clo_type,
                "clo_url": clo.clo_url,
                "clo_content": clo_content
            }

            clos_arr.append(clo_obj)
        
        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Clos fetched successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )