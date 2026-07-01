import json
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

# Standard AzTU assessment template used when a subject is created without one.
DEFAULT_ASSESSMENT = [
    {
        "form": "Cari qiymətləndirmə",
        "description": "Cari qiymətləndirmə - fənn üzrə tələbənin semestr müddətində fəaliyyətinin qiymətləndirilməsi olmaqla, mühazirə və məşğələ (laboratoriya) dərs materiallarının mənimsənilmə səviyyəsini qiymətləndirilir.",
        "score": "30 bal",
        "ftn": "FTN 1-5",
    },
    {
        "form": "Davamiyyət",
        "description": "Tələbə fənn üzrə dərslərin 25%-dən çoxunda iştirak etmədiyi halda imtahana buraxılmır.",
        "score": "10 bal",
        "ftn": "-",
    },
    {
        "form": "Tələbənin sərbəst işi",
        "description": "Tələbəyə fənn üzrə semestr ərzində 1 sərbəst işin (zəruri hallarda sərbəst işlərin sayı artırıla bilər) yerinə yetirilməsi tapşırığı verilir.",
        "score": "10 bal",
        "ftn": "FTN--",
    },
    {
        "form": "İmtahan",
        "description": "İmtahan şifahi, yazılı, yazılı-elektron, test üsulu ilə keçirilir",
        "score": "50 bal",
        "ftn": "FTN 1-5",
    },
]

async def _get_or_create_subject_translation(
    db: AsyncSession,
    subject_code: str,
    lang_code: str,
):
    """
    Return the CurriculaProgramTranslations row for (subject_code, lang_code).
    If lang_code is missing but az exists, machine-translate az -> requested lang
    and persist the new row so subsequent reads are O(1).
    """
    res = await db.execute(
        select(CurriculaProgramTranslations).where(
            CurriculaProgramTranslations.subject_code == subject_code,
            CurriculaProgramTranslations.language_code == lang_code,
        )
    )
    translation = res.scalar_one_or_none()
    if translation is not None:
        return translation

    if lang_code == "az":
        return None

    az_res = await db.execute(
        select(CurriculaProgramTranslations).where(
            CurriculaProgramTranslations.subject_code == subject_code,
            CurriculaProgramTranslations.language_code == "az",
        )
    )
    az_row = az_res.scalar_one_or_none()
    if az_row is None:
        return None

    try:
        translated_name = translate_to_english(az_row.subject_name) if lang_code == "en" else az_row.subject_name
        translated_desc = (
            translate_to_english(az_row.subject_description)
            if lang_code == "en" and az_row.subject_description
            else (az_row.subject_description or "")
        )
    except Exception:
        translated_name = az_row.subject_name
        translated_desc = az_row.subject_description or ""

    now = datetime.utcnow()
    new_row = CurriculaProgramTranslations(
        subject_code=subject_code,
        language_code=lang_code,
        subject_name=translated_name,
        subject_description=translated_desc,
        created_at=now,
        updated_at=now,
    )
    db.add(new_row)
    return new_row

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
        # Seed the standard assessment template when none is supplied.
        assessment_value = curricula_req.assessment
        if not assessment_value:
            assessment_value = json.dumps(DEFAULT_ASSESSMENT, ensure_ascii=False)

        new_curricula = CurriculaProgram(
            specialty_code=curricula_req.specialty_code,
            subject_code=curricula_req.subject_code,
            semester=curricula_req.semester,
            status=curricula_req.status,
            year=curricula_req.year,
            credit=curricula_req.credit,
            hours_per_week=curricula_req.hours_per_week,
            form_of_education=curricula_req.form_of_education,
            language_of_instruction=curricula_req.language_of_instruction,
            in_class_hours=curricula_req.in_class_hours,
            out_of_class_hours=curricula_req.out_of_class_hours,
            teaching_methods=curricula_req.teaching_methods,
            assessment=assessment_value,
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
            subject_details = await _get_or_create_subject_translation(
                db, curricula.subject_code, lang_code
            )

            subject_name = subject_details.subject_name if subject_details else curricula.subject_code

            subject_obj = {
                "subject_code": curricula.subject_code,
                "subject_name": subject_name,
                "semester": curricula.semester,
                "year": curricula.year,
                "hours_per_week": curricula.hours_per_week,
                "status": curricula.status,
                "credit": curricula.credit
            }

            subjects_arr.append(subject_obj)

        await db.commit()
        
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
        
        subject_translations = await _get_or_create_subject_translation(
            db, subject_code, lang_code
        )
        await db.commit()

        try:
            assessment_list = json.loads(subject.assessment) if subject.assessment else []
        except Exception:
            assessment_list = []

        subject_obj = {
            "subject_name": subject_translations.subject_name if subject_translations else subject_code,
            "subject_description": subject_translations.subject_description if subject_translations else "",
            "semester": subject.semester,
            "hours_per_week": subject.hours_per_week,
            "year": subject.year,
            "status": subject.status,
            "credit": subject.credit,
            "form_of_education": subject.form_of_education,
            "language_of_instruction": subject.language_of_instruction,
            "in_class_hours": subject.in_class_hours,
            "out_of_class_hours": subject.out_of_class_hours,
            "teaching_methods": subject.teaching_methods,
            "assessment": assessment_list
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
        if update_data.form_of_education is not None:
            curricula.form_of_education = update_data.form_of_education
            updated = True
        if update_data.language_of_instruction is not None:
            curricula.language_of_instruction = update_data.language_of_instruction
            updated = True
        if update_data.in_class_hours is not None:
            curricula.in_class_hours = update_data.in_class_hours
            updated = True
        if update_data.out_of_class_hours is not None:
            curricula.out_of_class_hours = update_data.out_of_class_hours
            updated = True
        if update_data.teaching_methods is not None:
            curricula.teaching_methods = update_data.teaching_methods
            updated = True
        if update_data.assessment is not None:
            curricula.assessment = update_data.assessment
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