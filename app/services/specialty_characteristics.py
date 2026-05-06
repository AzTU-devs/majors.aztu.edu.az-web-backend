from app.api.v1.schemas.specialty_characteristics import (
    SpecialtyCharacteristicsCreate,
    SpecialtyCharacteristicsUpdate,
)
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.models.speciality import Specialty
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.specialty_characteristics import SpecialtyCharacteristics
from app.models.translation.specialty_characteristics_translation import SpecialtyCharacteristicsTranslation

allowed_languages = ["en", "az"]

# GET SpecialtyCharacteristics by specialty_code
async def get_specialty_characteristics_by_specialty(db: AsyncSession, specialty_code: str, lang: str):
    if lang not in allowed_languages:
        return JSONResponse({"statusCode": 404, "message": "Invalid language code!"}, status_code=404)

    try:
        spec_q = await db.execute(select(Specialty).where(Specialty.specialty_code == specialty_code))
        specialty = spec_q.scalars().first()
        if not specialty:
            return JSONResponse({"statusCode": 404, "message": f"Specialty '{specialty_code}' not found!"}, status_code=404)
        
        result = await db.execute(
            select(SpecialtyCharacteristics, SpecialtyCharacteristicsTranslation)
            .join(SpecialtyCharacteristicsTranslation, SpecialtyCharacteristics.id == SpecialtyCharacteristicsTranslation.specialty_characteristic_id)
            .where(SpecialtyCharacteristics.id == SpecialtyCharacteristicsTranslation.specialty_characteristic_id)
            .where(SpecialtyCharacteristics.specialty_code == specialty_code)
            .where(SpecialtyCharacteristicsTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse({"statusCode": 204, "message": f"No specialty characteristics found for specialty '{specialty_code}' and language '{lang}'!"}, status_code=200)

        characteristics = []
        for char, translation in rows:
            characteristics.append({
                "id": char.id,
                "specialty_code": char.specialty_code,
                "language_code": translation.language_code,
                "program_desc": translation.program_desc,
                "degree_requirements": translation.degree_requirements
            })

        return JSONResponse({
            "statusCode": 200,
            "message": f"Specialty characteristics fetched successfully for specialty '{specialty_code}' and language '{lang}'!",
            "characteristics": characteristics
        }, status_code=200)

    except Exception as e:
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)

# GET all SpecialtyCharacteristics by language
async def get_all_specialty_characteristics(db: AsyncSession, lang: str):
    if lang not in allowed_languages:
        return JSONResponse({"statusCode": 404, "message": "Invalid language code!"}, status_code=404)

    try:
        result = await db.execute(
            select(SpecialtyCharacteristics, SpecialtyCharacteristicsTranslation)
            .join(SpecialtyCharacteristicsTranslation)
            .where(SpecialtyCharacteristicsTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse({"statusCode": 204, "message": f"No specialty characteristics found for language '{lang}'!"}, status_code=200)

        characteristics = []
        for char, translation in rows:
            characteristics.append({
                "id": char.id,
                "specialty_code": char.specialty_code,
                "language_code": translation.language_code,
                "program_desc": translation.program_desc,
                "degree_requirements": translation.degree_requirements
            })

        return JSONResponse({
            "statusCode": 200,
            "message": f"All specialty characteristics fetched successfully for language '{lang}'!",
            "characteristics": characteristics
        }, status_code=200)

    except Exception as e:
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)

# CREATE SpecialtyCharacteristics
async def create_specialty_characteristics(db: AsyncSession, char_data: SpecialtyCharacteristicsCreate):
    try:
        exist_spec_char_query = await db.execute(
            select(SpecialtyCharacteristics)
            .where(SpecialtyCharacteristics.specialty_code == char_data.specialty_code)
        )
        existing_spec_char = exist_spec_char_query.scalar_one_or_none()

        if existing_spec_char:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "Specialty characteristics already exists for provided specialty code."
                }, status_code=status.HTTP_409_CONFLICT
            )

        new_char = SpecialtyCharacteristics(
            specialty_code=char_data.specialty_code
        )
        db.add(new_char)
        await db.flush() 

        new_translation_en = SpecialtyCharacteristicsTranslation(
            specialty_characteristic_id=new_char.id,
            language_code="en",
            program_desc=translate_to_english(char_data.program_desc),
            degree_requirements=translate_to_english(char_data.degree_requirements)
        )
        new_translation_az = SpecialtyCharacteristicsTranslation(
            specialty_characteristic_id=new_char.id,
            language_code="az",
            program_desc=char_data.program_desc,
            degree_requirements=char_data.degree_requirements
        )
        db.add(new_translation_az)
        db.add(new_translation_en)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": f"Specialty characteristics created with translations."
            }, status_code=201
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)

# UPDATE SpecialtyCharacteristics
async def update_specialty_characteristics(db: AsyncSession, specialty_code: str, char_data: SpecialtyCharacteristicsUpdate):
    try:
        res = await db.execute(select(SpecialtyCharacteristics).where(SpecialtyCharacteristics.specialty_code == specialty_code))
        char = res.scalars().first()
        if not char:
            return JSONResponse({"statusCode": 404, "message": "Specialty characteristics not found!"}, status_code=404)

        tr_res_az = await db.execute(
            select(SpecialtyCharacteristicsTranslation)
            .where(SpecialtyCharacteristicsTranslation.specialty_characteristic_id == char.id)
            .where(SpecialtyCharacteristicsTranslation.language_code == "az")
        )
        tr_res_en = await db.execute(
            select(SpecialtyCharacteristicsTranslation)
            .where(SpecialtyCharacteristicsTranslation.specialty_characteristic_id == char.id)
            .where(SpecialtyCharacteristicsTranslation.language_code == "en")
        )
        tr_az = tr_res_az.scalars().first()
        tr_en = tr_res_en.scalars().first()
        if not tr_az or not tr_en:
            return JSONResponse({"statusCode": 404, "message": f"Translation for language' not found!"}, status_code=404)

        tr_az.program_desc = char_data.program_desc
        tr_az.degree_requirements = char_data.degree_requirements
        tr_en.program_desc = translate_to_english(char_data.program_desc)
        tr_en.degree_requirements = translate_to_english(char_data.degree_requirements)

        await db.commit()
        return JSONResponse({"statusCode": 200, "message": f"Specialty characteristics updated for language!"}, status_code=200)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)

# DELETE SpecialtyCharacteristics
async def delete_specialty_characteristics(db: AsyncSession, specialty_code: str):
    try:
        res = await db.execute(select(SpecialtyCharacteristics).where(SpecialtyCharacteristics.specialty_code == specialty_code))
        char = res.scalars().first()
        if not char:
            return JSONResponse({"statusCode": 404, "message": "Specialty characteristics not found!"}, status_code=404)

        await db.execute(SpecialtyCharacteristicsTranslation.__table__.delete().where(
            SpecialtyCharacteristicsTranslation.specialty_characteristic_id == char.id
        ))

        await db.delete(char)
        await db.commit()
        return JSONResponse({"statusCode": 200, "message": "Specialty characteristics and translations deleted successfully!"}, status_code=200)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)
