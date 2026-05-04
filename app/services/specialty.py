from sqlalchemy import func, and_
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
from app.api.v1.schemas.specialty import CreateSpecialty
from app.models.translation.cafedra_translations import CafedraTranslations
from app.models.translation.specialty_translations import SpecialtyTranslations

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

        specialties_result = await db.execute(query)
        specialties_list = specialties_result.scalars().all()

        if not specialties_list:
            return JSONResponse({"statusCode": 204, "message": "No specialty found"}, status_code=204)

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
            cafedra_name_obj = cafedra_query.scalar_one_or_none()
            cafedra_name = cafedra_name_obj.cafedra_name if cafedra_name_obj else None

            specialties_arr.append({
                "cafedra_name": cafedra_name,
                "specialty_code": specialty.specialty_code,
                "specialty_name": translation.specialty_name,
                "created_at": translation.created_at.isoformat() if translation.created_at else None
            })

        return JSONResponse({"statusCode": 200, "message": "Specialties fetched successfully", "specialties": specialties_arr})

    except Exception as e:
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)

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

    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def add_specialty(
    specialty_details: CreateSpecialty,
    db: AsyncSession = Depends(get_db)
):
    try:
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

        new_specialty_translations_az = SpecialtyTranslations(
            specialty_code = specialty_details.specialty_code,
            language_code = 'az',
            specialty_name = specialty_details.specialty_name,
            created_at = datetime.utcnow()
        )

        new_specialty_translations_en = SpecialtyTranslations(
            specialty_code = specialty_details.specialty_code,
            language_code = 'en',
            specialty_name = translate_to_english(specialty_details.specialty_name),
            created_at = datetime.utcnow()
        )

        db.add(new_specialty)
        db.add(new_specialty_translations_az)
        db.add(new_specialty_translations_en)
        await db.commit()
        await db.refresh(new_specialty)
        await db.refresh(new_specialty_translations_az)
        await db.refresh(new_specialty_translations_en)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "Specialty created successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )