import random
from sqlalchemy import func
from datetime import datetime
from app.db.session import get_db
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from fastapi import Depends, status, Query
from app.models.speciality import Specialty
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.curricula_program import *
from app.utils.translator import translate_to_english
from app.models.curricula_program import CurriculaProgram
from app.models.translation.curricula_program_translations import CurriculaProgramTranslations
import logging

logger = logging.getLogger(__name__)


def _internal_error() -> JSONResponse:
    return JSONResponse(
        {"statusCode": 500, "message": "Internal server error"},
        status_code=500,
    )

def generate_curricula_code():
    random_number = random.randint(10000, 99999)
    return f"CURRICULA-{random_number}"

async def add_curricula(
    curricula_req: CreateCurricula,
    db: AsyncSession = Depends(get_db)
):
    try:
        specialty_query = await db.execute(
            select(Specialty)
            .where(Specialty.specialty_code == curricula_req.specialty_code)
        )

        specialty = specialty_query.scalar_one_or_none()

        if not specialty:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Specialty not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        now = datetime.utcnow()
        new_curricula = CurriculaProgram(
            specialty_code=curricula_req.specialty_code,
            subject_code=curricula_req.subject_code,
            semester=curricula_req.semester,
            status=curricula_req.status,
            year=curricula_req.year,
            credit=curricula_req.credit,
            hours_per_week=curricula_req.hours_per_week,
            created_at=now,
            updated_at=now,
        )

        new_curricula_az = CurriculaProgramTranslations(
            subject_code=curricula_req.subject_code,
            subject_name=curricula_req.subject_name,
            subject_description=curricula_req.subject_desc,
            language_code="az",
            created_at=now,
            updated_at=now,
        )

        db.add(new_curricula)
        db.add(new_curricula_az)
        await db.commit()
        await db.refresh(new_curricula)
        await db.refresh(new_curricula_az)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "Curricula created successfully."
            }, status_code=status.HTTP_201_CREATED
        )

    except Exception:
        logger.exception("Error in add_curricula")
        return _internal_error()

async def get_curricula_by_specialty(
    specialty_code: str,
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=0),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        total_query = await db.execute(
            select(func.count())
            .select_from(CurriculaProgram)
            .where(CurriculaProgram.specialty_code == specialty_code)
        )
        total = total_query.scalar_one()

        curricula_query = await db.execute(
            select(CurriculaProgram)
            .where(CurriculaProgram.specialty_code == specialty_code)
            .offset(start)
            .limit(end - start)
        )

        curriculas = curricula_query.scalars().all()

        if not curriculas:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "No curricula found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        subjects_arr = []

        for curricula in curriculas:
            subject_query = await db.execute(
                select(CurriculaProgramTranslations)
                .where(
                    CurriculaProgramTranslations.subject_code == curricula.subject_code,
                    CurriculaProgramTranslations.language_code == lang_code
                )
            )

            subject_details =subject_query.scalar_one_or_none()

            subject_obj = {
                "subject_code": curricula.subject_code,
                "subject_name": subject_details.subject_name,
                "semester": curricula.semester,
                "year": curricula.year,
                "hours_per_week": curricula.hours_per_week,
                "status": curricula.status,
                "credit": curricula.credit
            }

            subjects_arr.append(subject_obj)
        
        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Subjects fetched successfully." ,
                "subjects": subjects_arr,
                "total_subjects": total
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception:
        logger.exception("Error in curricula service")
        return _internal_error()

async def get_curricula_by_subject(
    subject_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        subject_query = await db.execute(
            select(CurriculaProgram)
            .where(CurriculaProgram.subject_code == subject_code)
        )

        subject = subject_query.scalar_one_or_none()

        if not subject:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Subject not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        subject_translation_query = await db.execute(
            select(CurriculaProgramTranslations)
            .where(
                CurriculaProgramTranslations.subject_code == subject_code,
                CurriculaProgramTranslations.language_code == lang_code
            )
        )

        subject_translations = subject_translation_query.scalar_one_or_none()

        subject_obj = {
            "subject_name": subject_translations.subject_name,
            "subject_description": subject_translations.subject_description,
            "semester": subject.semester,
            "hours_per_week": subject.hours_per_week,
            "year": subject.year,
            "status": subject.status,
            "credit": subject.credit
        }

        return JSONResponse(
            content={
                "statusCode": 200,
                "subject_details": subject_obj
            }, status_code=status.HTTP_200_OK
        )
    except Exception:
        logger.exception("Error in curricula service")
        return _internal_error()

async def delete_curricula(
    subject_code: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        subject_query = await db.execute(
            select(CurriculaProgram)
            .where(CurriculaProgram.subject_code == subject_code)
        )

        curricula = subject_query.scalar_one_or_none()

        if not curricula:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Subject not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        curricula_translation_query = await db.execute(
            select(CurriculaProgramTranslations)
            .where(CurriculaProgramTranslations.subject_code == subject_code)
        )

        curricula_translations = curricula_translation_query.scalars().all()

        for translation in curricula_translations:
            await db.delete(translation)
        await db.delete(curricula)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Curricula deleted successfully."
            }, status_code=status.HTTP_200_OK
        )

    except Exception:
        logger.exception("Error in curricula service")
        return _internal_error()
async def update_curricula(
    subject_code: str,
    update_data: UpdateCurricula,
    db: AsyncSession
):
    try:
        logger.debug(f"Received update_data: {update_data}")
        logger.debug(f"Types of update_data fields: semester={type(update_data.semester)}, status={type(update_data.status)}, year={type(update_data.year)}, credit={type(update_data.credit)}, hours_per_week={type(update_data.hours_per_week)}, subject_name={type(update_data.subject_name)}, subject_description={type(update_data.subject_description)}")
        
        subject_query = await db.execute(
            select(CurriculaProgram).where(CurriculaProgram.subject_code == subject_code)
        )
        curricula = subject_query.scalar_one_or_none()
        if not curricula:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Subject not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        updated = False
        if update_data.semester is not None:
            curricula.semester = update_data.semester
            updated = True
        if update_data.status is not None:
            curricula.status = update_data.status
            updated = True
        if update_data.year is not None:
            curricula.year = update_data.year
            updated = True
        if update_data.credit is not None:
            curricula.credit = update_data.credit
            updated = True
        if update_data.hours_per_week is not None:
            curricula.hours_per_week = update_data.hours_per_week
            updated = True

        if (update_data.subject_name is not None) or (update_data.subject_description is not None):
            translations_query = await db.execute(
                select(CurriculaProgramTranslations).where(CurriculaProgramTranslations.subject_code == subject_code)
            )
            translations = translations_query.scalars().all()
            for translation in translations:
                if update_data.subject_name is not None:
                    translation.subject_name = update_data.subject_name.get(translation.language_code, translation.subject_name)
                    updated = True
                if update_data.subject_description is not None:
                    translation.subject_description = update_data.subject_description.get(translation.language_code, translation.subject_description)
                    updated = True

        if updated:
            await db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Curricula updated successfully."
            }, status_code=status.HTTP_200_OK
        )
    except Exception:
        logger.exception("Error in curricula service")
        return _internal_error()