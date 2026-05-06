import random
from datetime import datetime
from app.models.tlo import Tlo
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.api.v1.schemas.tlo import CreateTlo
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translation.tlo_translation import TloTranslations
from app.models.curricula_program import CurriculaProgram

def generate_tlo_code():
    random_number = random.randint(10000, 99999)
    return f"tlo-{random_number}"

async def add_tlo(
    tlo_request: CreateTlo,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        subject_query = await db.execute(
            select(CurriculaProgram)
            .where(CurriculaProgram.subject_code == tlo_request.subject_code)
        )

        subject = subject_query.scalars().first()

        if not subject:
            return JSONResponse(
                content={
                   "status_code": 404,
                   "message": "Subject not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        tlo_code = generate_tlo_code()

        new_tlo = Tlo(
            subject_code=tlo_request.subject_code,
            tlo_code=tlo_code,
            created_at=datetime.utcnow()
        )

        new_tlo_az = TloTranslations(
            tlo_code=tlo_code,
            language_code="az",
            tlo_content=tlo_request.tlo_content,
            created_at=datetime.utcnow()
        )

        new_tlo_en = TloTranslations(
            tlo_code=tlo_code,
            language_code="en",
            tlo_content=translate_to_english(tlo_request.tlo_content),
            created_at=datetime.utcnow()
        )

        db.add(new_tlo)
        db.add(new_tlo_az)
        db.add(new_tlo_en)
        await db.commit()
        await db.refresh(new_tlo)
        await db.refresh(new_tlo_az)
        await db.refresh(new_tlo_en)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "tlo added successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_tlo_by_subject_code(
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
        
        tlo_query = await db.execute(
            select(Tlo)
            .where(Tlo.subject_code == subject_code)
        )

        tlos = tlo_query.scalars().all()

        if not tlos:
            return JSONResponse(
                content={
                   "status_code": 204,
                   "message": "No content"
                }, status_code=status.HTTP_200_OK
            )
        
        tlos_arr = []

        for tlo in tlos:
            tlo_content_query = await db.execute(
                select(TloTranslations)
                .where(
                    TloTranslations.tlo_code == tlo.tlo_code,
                    TloTranslations.language_code == lang_code
                )
            )

            tlo_content = tlo_content_query.scalar_one_or_none().tlo_content

            tlo_obj = {
                "subject_code": subject_code,
                "tlo_code": tlo.tlo_code,
                "tlo_type": tlo.tlo_type,
                "tlo_url": tlo.tlo_url,
                "tlo_content": tlo_content
            }

            tlos_arr.append(tlo_obj)
        
        return JSONResponse(
            content={
                "status_code": 201,
                "message": "tlos fetched successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )