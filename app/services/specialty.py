import logging
from sqlalchemy import func, and_, text, inspect as sa_inspect
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.db.session import get_db
from sqlalchemy.future import select
from app.models.cafedra import Cafedra
from app.models.faculty import Faculty
from fastapi.responses import JSONResponse
from fastapi import Depends, status, Query
from app.utils.language import get_language
from app.models.speciality import Specialty
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.api.v1.schemas.specialty import CreateSpecialty, UpdateSpecialty
from app.models.translation.cafedra_translations import CafedraTranslations
from app.models.translation.specialty_translations import SpecialtyTranslations

logger = logging.getLogger(__name__)


def _internal_error() -> JSONResponse:
    return JSONResponse(
        {"statusCode": 500, "message": "Internal server error"},
        status_code=500,
    )

async def get_specialties(
    faculty_code: str = Query(None),
    cafedra_code: str = Query(None),
    specialty_name: str = Query(None),
    specialty_code: str = Query(None),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Base Specialty query
        query = select(Specialty)

        # Join with Cafedra and Faculty for filtering by codes
        if faculty_code or cafedra_code:
            query = query.join(Cafedra, Specialty.cafedra_code == Cafedra.cafedra_code)\
                         .join(Faculty, Cafedra.faculty_code == Faculty.faculty_code)

        # Apply filters
        filters = []
        if faculty_code:
            filters.append(Faculty.faculty_code == faculty_code)
        if cafedra_code:
            filters.append(Cafedra.cafedra_code == cafedra_code)
        if specialty_code:
            filters.append(Specialty.specialty_code == specialty_code)

        if filters:
            query = query.where(and_(*filters))

        # Stable order so the list (and its syllabus order) never shifts on edit/delete.
        query = query.order_by(Specialty.id)

        specialties_result = await db.execute(query)
        specialties_list = specialties_result.scalars().all()

        if not specialties_list:
            return JSONResponse({"statusCode": 204, "message": "No specialty found"}, status_code=200)

        # Get translations for specialties
        specialty_codes = [s.specialty_code for s in specialties_list]
        translation_query = select(SpecialtyTranslations).where(
            and_(
                SpecialtyTranslations.specialty_code.in_(specialty_codes),
                SpecialtyTranslations.language_code == lang_code
            )
        )
        if specialty_name:
            translation_query = translation_query.where(SpecialtyTranslations.specialty_name == specialty_name)

        translations_result = await db.execute(translation_query)
        translations = translations_result.scalars().all()
        translations_map = {t.specialty_code: t for t in translations}

        specialties_arr = []
        for specialty in specialties_list:
            translation = translations_map.get(specialty.specialty_code)
            if not translation:
                continue

            # Get Cafedra name
            cafedra_query = await db.execute(
                select(CafedraTranslations).where(
                    CafedraTranslations.cafedra_code == specialty.cafedra_code,
                    CafedraTranslations.lang_code == lang_code
                )
            )
            cafedra_name_obj = cafedra_query.scalars().first()
            cafedra_name = cafedra_name_obj.cafedra_name if cafedra_name_obj else None

            specialties_arr.append({
                "cafedra_name": cafedra_name,
                "specialty_code": specialty.specialty_code,
                "specialty_name": translation.specialty_name,
                "created_at": translation.created_at.isoformat() if translation.created_at else None
            })

        return JSONResponse({"statusCode": 200, "message": "Specialties fetched successfully", "specialties": specialties_arr})

    except Exception:
        logger.exception("Error in specialty service")
        return _internal_error()

async def get_specialties_by_cafedra(
    cafedra_code: str,
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=1),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        total_query = await db.execute(
            select(func.count(Specialty.specialty_code))
            .where(Specialty.cafedra_code == cafedra_code)
        )
        total_count = total_query.scalar()

        if total_count == 0:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Specialty not found.",
                    "total": 0,
                    "specialties": []
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        specialty_query = await db.execute(
            select(Specialty)
            .where(Specialty.cafedra_code == cafedra_code)
            .order_by(Specialty.id)
            .offset(start)
            .limit(end - start)
        )
        specialties = specialty_query.scalars().all()

        specialty_codes = [s.specialty_code for s in specialties]
        translations_query = await db.execute(
            select(SpecialtyTranslations)
            .where(
                SpecialtyTranslations.specialty_code.in_(specialty_codes),
                SpecialtyTranslations.language_code == lang_code
            )
        )
        translations = translations_query.scalars().all()
        translations_map = {t.specialty_code: t for t in translations}

        specialty_details = []
        for specialty in specialties:
            t = translations_map.get(specialty.specialty_code)
            specialty_obj = {
                "specialty_code": t.specialty_code,
                "specialty_name": t.specialty_name,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            specialty_details.append(specialty_obj)

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Specialties fetched successfully.",
                "total": total_count,
                "specialties": specialty_details,
            }, status_code=status.HTTP_200_OK
        )

    except Exception:
        logger.exception("Error in specialty service")
        return _internal_error()

async def add_specialty(
    specialty_details: CreateSpecialty,
    db: AsyncSession = Depends(get_db)
):
    try:
        from app.utils.code_validator import is_valid_code, CODE_RULE_MESSAGE
        specialty_details.specialty_code = specialty_details.specialty_code.strip()
        if not is_valid_code(specialty_details.specialty_code):
            return JSONResponse(
                content={"statusCode": 400, "message": CODE_RULE_MESSAGE},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        exists_specialty_code = await db.execute(
            select(Specialty)
            .where(Specialty.specialty_code == specialty_details.specialty_code)
        )

        exists_specialty_name = await db.execute(
            select(SpecialtyTranslations)
            .where(SpecialtyTranslations.specialty_name == specialty_details.specialty_name)
        )

        if exists_specialty_code.scalar_one_or_none() or exists_specialty_name.scalar_one_or_none():
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "Specialty already exists."
                }, status_code=status.HTTP_409_CONFLICT
            )
        
        new_specialty = Specialty(
            cafedra_code=specialty_details.cafedra_code,
            specialty_code=specialty_details.specialty_code,
            created_at=datetime.utcnow(),
            updated_at=None
        )

        now = datetime.utcnow()
        new_specialty_translations_az = SpecialtyTranslations(
            specialty_code=specialty_details.specialty_code,
            language_code='az',
            specialty_name=specialty_details.specialty_name,
            created_at=now,
        )

        new_specialty_translations_en = SpecialtyTranslations(
            specialty_code=specialty_details.specialty_code,
            language_code='en',
            specialty_name=translate_to_english(specialty_details.specialty_name),
            created_at=now,
        )

        db.add(new_specialty)
        db.add(new_specialty_translations_az)
        db.add(new_specialty_translations_en)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "Specialty code or name already exists.",
                },
                status_code=status.HTTP_409_CONFLICT,
            )

        await db.refresh(new_specialty)
        await db.refresh(new_specialty_translations_az)
        await db.refresh(new_specialty_translations_en)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "Specialty created successfully."
            }, status_code=status.HTTP_201_CREATED
        )

    except Exception:
        logger.exception("Error in specialty service")
        return _internal_error()

# Child tables whose specialty_code must follow a specialty-code rename.
_SPECIALTY_CHILD_TABLES = [
    "plo",
    "graduate_career_opportunities",
    "competency",
    "curricula_program",
    "specialty_characteristics",
    "specialty_translations",
    "slo",  # legacy/unused, repointed only if the table still exists
]


async def update_specialty(
    specialty_code: str,
    payload: UpdateSpecialty,
    db: AsyncSession,
):
    """Edit a specialty's name and/or its code.

    Renaming the code is a primary-key change referenced by many child tables,
    so under Postgres' immediate FK checks we insert a new specialties row,
    repoint every child table to the new code, then drop the old row (works on
    SQLite too).
    """
    try:
        res = await db.execute(
            select(Specialty).where(Specialty.specialty_code == specialty_code)
        )
        specialty = res.scalars().first()
        if not specialty:
            return JSONResponse(
                content={"statusCode": 404, "message": "Specialty not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        target_code = specialty_code
        new_code = payload.new_specialty_code
        if new_code is not None:
            new_code = new_code.strip()

        # ---- code rename ---------------------------------------------------
        if new_code and new_code != specialty_code:
            from app.utils.code_validator import is_valid_code, CODE_RULE_MESSAGE
            if not is_valid_code(new_code):
                return JSONResponse(
                    content={"statusCode": 400, "message": CODE_RULE_MESSAGE},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            taken = await db.execute(
                select(Specialty).where(Specialty.specialty_code == new_code)
            )
            if taken.scalars().first():
                return JSONResponse(
                    content={"statusCode": 409, "message": "Specialty code already in use."},
                    status_code=status.HTTP_409_CONFLICT,
                )

            # Only touch child tables that actually exist in this database.
            conn = await db.connection()
            existing = set(
                await conn.run_sync(lambda c: sa_inspect(c).get_table_names())
            )

            now = datetime.utcnow()
            await db.execute(
                text(
                    "INSERT INTO specialties (cafedra_code, specialty_code, created_at, updated_at) "
                    "SELECT cafedra_code, :new, created_at, :now FROM specialties WHERE specialty_code = :old"
                ),
                {"new": new_code, "old": specialty_code, "now": now},
            )
            for table in _SPECIALTY_CHILD_TABLES:
                if table in existing:
                    await db.execute(
                        text(f"UPDATE {table} SET specialty_code = :new WHERE specialty_code = :old"),
                        {"new": new_code, "old": specialty_code},
                    )
            await db.execute(
                text("DELETE FROM specialties WHERE specialty_code = :old"),
                {"old": specialty_code},
            )
            target_code = new_code

        # ---- name change ---------------------------------------------------
        if payload.specialty_name is not None:
            try:
                en_name = translate_to_english(payload.specialty_name)
            except Exception:
                en_name = payload.specialty_name
            now = datetime.utcnow()
            for lang, name in (("az", payload.specialty_name), ("en", en_name)):
                tr_res = await db.execute(
                    select(SpecialtyTranslations).where(
                        SpecialtyTranslations.specialty_code == target_code,
                        SpecialtyTranslations.language_code == lang,
                    )
                )
                tr = tr_res.scalars().first()
                if tr:
                    tr.specialty_name = name
                else:
                    db.add(SpecialtyTranslations(
                        specialty_code=target_code,
                        language_code=lang,
                        specialty_name=name,
                        created_at=now,
                    ))

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return JSONResponse(
                content={"statusCode": 409, "message": "Specialty code or name already exists."},
                status_code=status.HTTP_409_CONFLICT,
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Specialty updated successfully.",
                "specialty_code": target_code,
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        await db.rollback()
        logger.exception("Error in update_specialty")
        return _internal_error()


async def delete_specialty(
    specialty_code: str,
    db: AsyncSession,
):
    try:
        specialty_query = await db.execute(
            select(Specialty).where(Specialty.specialty_code == specialty_code)
        )
        specialty = specialty_query.scalars().first()

        if not specialty:
            return JSONResponse(
                content={"statusCode": 404, "message": "Specialty not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        translations_query = await db.execute(
            select(SpecialtyTranslations).where(
                SpecialtyTranslations.specialty_code == specialty_code
            )
        )
        for tr in translations_query.scalars().all():
            await db.delete(tr)

        await db.delete(specialty)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Specialty deleted successfully.",
                "specialty_code": specialty_code,
            },
            status_code=status.HTTP_200_OK,
        )

    except Exception:
        logger.exception("Error in delete_specialty")
        return _internal_error()


async def get_specialty_by_specialty_code(
    specialty_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        specialty_query = await db.execute(
            select(SpecialtyTranslations)
            .where(
                SpecialtyTranslations.specialty_code == specialty_code,
                SpecialtyTranslations.language_code == lang_code
            )
        )

        specialty = specialty_query.scalar_one_or_none()

        if not specialty:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Specialty not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Specialty fetched successfully.",
                "specialty_name": specialty.specialty_name
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception:
        logger.exception("Error in specialty service")
        return _internal_error()