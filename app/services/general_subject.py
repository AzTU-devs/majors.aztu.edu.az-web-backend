import json
import logging
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cafedra import Cafedra
from app.models.speciality import Specialty
from app.models.curricula_program import CurriculaProgram
from app.models.translation.curricula_program_translations import CurriculaProgramTranslations
from app.models.translation.specialty_translations import SpecialtyTranslations
from app.services.curricula_program import _to_english, DEFAULT_ASSESSMENT
from app.utils.code_validator import is_valid_code, CODE_RULE_MESSAGE
from app.api.v1.schemas.general_subject import CreateGeneralSubject

logger = logging.getLogger(__name__)


def _internal_error() -> JSONResponse:
    return JSONResponse(
        {"statusCode": 500, "message": "Internal server error"},
        status_code=500,
    )


async def create_general_subject(payload: CreateGeneralSubject, db: AsyncSession):
    """Create a general subject (owned by one cafedra) and assign it to
    specialties of other cafedras — one curricula_program row per specialty,
    sharing a single subject_code + translations."""
    try:
        cafedra = (
            await db.execute(select(Cafedra).where(Cafedra.cafedra_code == payload.owner_cafedra_code))
        ).scalar_one_or_none()
        if not cafedra:
            return JSONResponse(
                content={"statusCode": 404, "message": "Cafedra not found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if not cafedra.general_subjects_enabled:
            return JSONResponse(
                content={"statusCode": 403, "message": "General subjects module is not enabled for this cafedra."},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        payload.subject_code = payload.subject_code.strip()
        if not is_valid_code(payload.subject_code):
            return JSONResponse(
                content={"statusCode": 400, "message": CODE_RULE_MESSAGE},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        exists = (
            await db.execute(select(CurriculaProgram).where(CurriculaProgram.subject_code == payload.subject_code))
        ).scalars().first()
        if exists:
            return JSONResponse(
                content={"statusCode": 409, "message": "Subject code already exists."},
                status_code=status.HTTP_409_CONFLICT,
            )

        target_specialties = list(dict.fromkeys(payload.specialty_codes))  # de-dupe, keep order
        if not target_specialties:
            return JSONResponse(
                content={"statusCode": 400, "message": "Assign at least one specialty."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        found = set(
            (await db.execute(
                select(Specialty.specialty_code).where(Specialty.specialty_code.in_(target_specialties))
            )).scalars().all()
        )
        missing = [c for c in target_specialties if c not in found]
        if missing:
            return JSONResponse(
                content={"statusCode": 404, "message": f"Specialties not found: {', '.join(missing)}"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        now = datetime.utcnow()
        assessment_value = payload.assessment or json.dumps(DEFAULT_ASSESSMENT, ensure_ascii=False)

        for spec_code in target_specialties:
            db.add(CurriculaProgram(
                specialty_code=spec_code,
                subject_code=payload.subject_code,
                is_general=True,
                owner_cafedra_code=payload.owner_cafedra_code,
                semester=payload.semester,
                status=payload.status,
                year=payload.year,
                credit=payload.credit,
                hours_per_week=payload.hours_per_week,
                form_of_education=payload.form_of_education,
                language_of_instruction=payload.language_of_instruction,
                in_class_hours=payload.in_class_hours,
                out_of_class_hours=payload.out_of_class_hours,
                teaching_methods=payload.teaching_methods,
                assessment=assessment_value,
                created_at=now,
                updated_at=now,
            ))

        db.add(CurriculaProgramTranslations(
            subject_code=payload.subject_code,
            language_code="az",
            subject_name=payload.subject_name,
            subject_description=payload.subject_desc,
            created_at=now,
            updated_at=now,
        ))
        db.add(CurriculaProgramTranslations(
            subject_code=payload.subject_code,
            language_code="en",
            subject_name=_to_english(payload.subject_name, payload.language_of_instruction),
            subject_description=_to_english(payload.subject_desc, payload.language_of_instruction),
            created_at=now,
            updated_at=now,
        ))

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return JSONResponse(
                content={"statusCode": 409, "message": "Subject already exists."},
                status_code=status.HTTP_409_CONFLICT,
            )

        return JSONResponse(
            content={"statusCode": 201, "message": "General subject created."},
            status_code=status.HTTP_201_CREATED,
        )
    except Exception:
        await db.rollback()
        logger.exception("Error in create_general_subject")
        return _internal_error()


async def get_general_subjects_by_cafedra(cafedra_code: str, lang_code: str, db: AsyncSession):
    """List general subjects created by a cafedra, grouped by subject, with the
    specialties each is assigned to."""
    try:
        rows = (
            await db.execute(
                select(CurriculaProgram)
                .where(
                    CurriculaProgram.owner_cafedra_code == cafedra_code,
                    CurriculaProgram.is_general == True,  # noqa: E712
                )
                .order_by(CurriculaProgram.id)
            )
        ).scalars().all()

        grouped = {}
        for row in rows:
            grouped.setdefault(row.subject_code, []).append(row)

        result = []
        for subject_code, items in grouped.items():
            name_row = (
                await db.execute(
                    select(CurriculaProgramTranslations).where(
                        CurriculaProgramTranslations.subject_code == subject_code,
                        CurriculaProgramTranslations.language_code == lang_code,
                    )
                )
            ).scalars().first()
            subject_name = name_row.subject_name if name_row else subject_code

            specialties = []
            for item in items:
                spec_name_row = (
                    await db.execute(
                        select(SpecialtyTranslations).where(
                            SpecialtyTranslations.specialty_code == item.specialty_code,
                            SpecialtyTranslations.language_code == lang_code,
                        )
                    )
                ).scalars().first()
                specialties.append({
                    "specialty_code": item.specialty_code,
                    "specialty_name": spec_name_row.specialty_name if spec_name_row else item.specialty_code,
                })

            first = items[0]
            result.append({
                "subject_code": subject_code,
                "subject_name": subject_name,
                "semester": first.semester,
                "credit": first.credit,
                "year": first.year,
                "specialties": specialties,
            })

        return JSONResponse(
            content={"statusCode": 200, "general_subjects": result},
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error in get_general_subjects_by_cafedra")
        return _internal_error()


async def delete_general_subject(subject_code: str, db: AsyncSession):
    """Remove a general subject from every specialty it was assigned to."""
    try:
        rows = (
            await db.execute(
                select(CurriculaProgram).where(
                    CurriculaProgram.subject_code == subject_code,
                    CurriculaProgram.is_general == True,  # noqa: E712
                )
            )
        ).scalars().all()
        if not rows:
            return JSONResponse(
                content={"statusCode": 404, "message": "General subject not found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        translations = (
            await db.execute(
                select(CurriculaProgramTranslations).where(
                    CurriculaProgramTranslations.subject_code == subject_code
                )
            )
        ).scalars().all()
        for tr in translations:
            await db.delete(tr)
        for row in rows:
            await db.delete(row)
        await db.commit()

        return JSONResponse(
            content={"statusCode": 200, "message": "General subject deleted."},
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        await db.rollback()
        logger.exception("Error in delete_general_subject")
        return _internal_error()
