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

# language_of_instruction value -> Google Translate source code.
# 1 Azerbaijani, 2 English, 3 Russian, 4 German, 5 Turkish.
_LANG_SOURCE = {1: "az", 2: "en", 3: "ru", 4: "de", 5: "tr"}


def _to_english(text, language_of_instruction):
    """Translate ``text`` into English from the subject's instruction language.

    Falls back to the original text on any failure. When the subject is already
    taught in English no translation is attempted.
    """
    if not text:
        return text or ""
    source = _LANG_SOURCE.get(language_of_instruction, "az")
    if source == "en":
        return text
    try:
        return translate_to_english(text, source_lang=source)
    except Exception:
        return text


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

    if lang_code == "en":
        # Translate from the subject's actual instruction language (ru/de/tr/az),
        # not always Azerbaijani, so a Russian/German/Turkish name renders right.
        loi_res = await db.execute(
            select(CurriculaProgram.language_of_instruction).where(
                CurriculaProgram.subject_code == subject_code
            )
        )
        language_of_instruction = loi_res.scalar_one_or_none()
        translated_name = _to_english(az_row.subject_name, language_of_instruction)
        translated_desc = _to_english(az_row.subject_description, language_of_instruction)
    else:
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
        # Normalise the codes so a stray leading/trailing space can't produce a
        # subject that lists fine but 404s on lookup by its exact code.
        curricula_req.subject_code = curricula_req.subject_code.strip()
        curricula_req.specialty_code = curricula_req.specialty_code.strip()

        from app.utils.code_validator import is_valid_code, CODE_RULE_MESSAGE
        if not is_valid_code(curricula_req.subject_code):
            return JSONResponse(
                content={"statusCode": 400, "message": CODE_RULE_MESSAGE},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

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

        # Build the English translation from the actual instruction language
        # (Azerbaijani / Russian / German / Turkish), or use the text as-is when
        # the subject is already taught in English.
        new_curricula_en = CurriculaProgramTranslations(
            subject_code=curricula_req.subject_code,
            subject_name=_to_english(curricula_req.subject_name, curricula_req.language_of_instruction),
            subject_description=_to_english(curricula_req.subject_desc, curricula_req.language_of_instruction),
            language_code="en",
            created_at=now,
            updated_at=now,
        )

        db.add(new_curricula)
        db.add(new_curricula_az)
        db.add(new_curricula_en)

        # Assign the same subject to any additional specialties (possibly in
        # other cafedras) — one curricula row each, sharing the translations.
        extra_codes = [
            c for c in dict.fromkeys(curricula_req.additional_specialty_codes or [])
            if c and c != curricula_req.specialty_code
        ]
        if extra_codes:
            found = set(
                (await db.execute(
                    select(Specialty.specialty_code).where(Specialty.specialty_code.in_(extra_codes))
                )).scalars().all()
            )
            for code in extra_codes:
                if code not in found:
                    continue
                db.add(CurriculaProgram(
                    specialty_code=code,
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
                ))

        await db.commit()
        await db.refresh(new_curricula)
        await db.refresh(new_curricula_az)
        await db.refresh(new_curricula_en)

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
            .order_by(CurriculaProgram.id)
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
                "credit": curricula.credit,
                "is_general": bool(curricula.is_general),
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

        # .first() (not scalar_one_or_none) so an accidental duplicate code
        # returns the subject instead of raising a 500.
        subject = subject_query.scalars().first()

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

        # A subject may be assigned to several specialties (multiple rows share
        # the subject_code); delete them all along with the shared translations.
        curriculas = subject_query.scalars().all()

        if not curriculas:
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
        for curricula in curriculas:
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
        # A subject may be assigned to several specialties (rows sharing the
        # subject_code); apply the field edits to all of them.
        curriculas = subject_query.scalars().all()
        if not curriculas:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Subject not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        curricula = curriculas[0]

        updated = False
        field_updates = {}
        for field in (
            "semester", "status", "year", "credit", "hours_per_week",
            "form_of_education", "language_of_instruction",
            "in_class_hours", "out_of_class_hours", "teaching_methods", "assessment",
        ):
            value = getattr(update_data, field)
            if value is not None:
                field_updates[field] = value

        if field_updates:
            for row in curriculas:
                for field, value in field_updates.items():
                    setattr(row, field, value)
            updated = True

        if (update_data.subject_name is not None) or (update_data.subject_description is not None) or (update_data.language_of_instruction is not None):
            translations_query = await db.execute(
                select(CurriculaProgramTranslations).where(CurriculaProgramTranslations.subject_code == subject_code)
            )
            translations = {t.language_code: t for t in translations_query.scalars().all()}

            # Apply the incoming per-language name/description edits.
            for lang_code, translation in translations.items():
                if update_data.subject_name is not None and lang_code in update_data.subject_name:
                    translation.subject_name = update_data.subject_name.get(lang_code, translation.subject_name)
                    updated = True
                if update_data.subject_description is not None and lang_code in update_data.subject_description:
                    translation.subject_description = update_data.subject_description.get(lang_code, translation.subject_description)
                    updated = True

            # Regenerate English from the primary (az) row using the subject's
            # instruction language, unless the caller explicitly supplied English.
            az_tr = translations.get("az")
            en_tr = translations.get("en")
            if az_tr is not None and en_tr is not None:
                supplied_en_name = update_data.subject_name is not None and "en" in update_data.subject_name
                supplied_en_desc = update_data.subject_description is not None and "en" in update_data.subject_description
                if not supplied_en_name:
                    en_tr.subject_name = _to_english(az_tr.subject_name, curricula.language_of_instruction)
                    updated = True
                if not supplied_en_desc:
                    en_tr.subject_description = _to_english(az_tr.subject_description, curricula.language_of_instruction)
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