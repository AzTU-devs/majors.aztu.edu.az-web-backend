import random
import sqlalchemy as sa
from app.models.slo import Slo
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.models.speciality import Specialty
from app.api.v1.schemas.slo import SloCreate
from app.models.university import University
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translation.slo_translations import SloTranslation


allowed_languages = ["en","az"]

def generate_slo_code():
    random_number = random.randint(10000, 99999)
    return f"SLO-{random_number}"

async def get_all_slos(db: AsyncSession, lang: str = Depends(get_language)):
    if lang not in allowed_languages:
        return JSONResponse(
            content={
                "statusCode": 404,
                "message":"Invalid language code!"
            },
            status_code=404
        )
    try:
        result = await db.execute(
            select(Slo, SloTranslation)
            .join(SloTranslation, Slo.slo_code == SloTranslation.slo_code)
            .where(SloTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": f"No SLO found for language '{lang}'!"
                },
                status_code=204
            )

        slos = []
        for slo, translation in rows:
            slos.append({
                "id": slo.id,
                "specialty_code": slo.specialty_code,
                "slo_code": slo.slo_code,
                "language_code": translation.language_code,
                "slo_content": translation.slo_content
            })

        return JSONResponse(
            content={
                "statusCode": 200,
                "message":  f"All SLOs fetched successfully for language '{lang}'!",
                "slos": slos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )


# GET by specialty_code
async def get_slos_by_specialty(
    specialty_code: str,
    lang: str,
    db: AsyncSession
):
    if lang not in allowed_languages:
        return JSONResponse(
            content={"statusCode": 404, "message": "Invalid language code!"},
            status_code=404
        )

    try:
        spec_q = await db.execute(
            select(Specialty).where(Specialty.specialty_code == specialty_code)
        )
        if not spec_q.scalars().first():
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Specialty not found!"
                },
                status_code=404
            )
        query = (
            select(Slo, SloTranslation)
            .join(SloTranslation, Slo.slo_code == SloTranslation.slo_code)
            .where(Slo.specialty_code == specialty_code)
            .where(SloTranslation.language_code == lang)
        )

        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No SLO found for this specialty!",
                },
                status_code=204
            )

        slos = []
        for slo, translation in rows:
            slos.append({
                "id": slo.id,
                "specialty_code": slo.specialty_code,
                "slo_code": slo.slo_code,
                "language_code": translation.language_code,
                "slo_content": translation.slo_content
            })

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "SLOs fetched successfully!",
                "slos": slos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )

# Create SLO with translations
async def create_slo(db: AsyncSession, slo_data):
    try:
        specialty_q = await db.execute(
            select(Specialty).where(Specialty.specialty_code == slo_data.specialty_code)
        )
        if not specialty_q.scalars().first():
            return JSONResponse(
                content={"statusCode": 404, "message": "Specialty code does not exist!"},
                status_code=404
            )
        
        slo_code = generate_slo_code()

        new_slo = Slo(
            specialty_code=slo_data.specialty_code,
            slo_code=slo_code,
        )
        db.add(new_slo)

        new_translation_az = SloTranslation(
            slo_code=slo_code,
            language_code="az",
            slo_content=slo_data.slo_content,
        )
        new_translation_en = SloTranslation(
            slo_code=slo_code,
            language_code="en",
            slo_content=translate_to_english(slo_data.slo_content),
        )
        db.add(new_translation_az)
        db.add(new_translation_en)

        await db.commit()
        return JSONResponse(
            content={
                "statusCode": 201,
                "message": f"SLO created successfully with translation!"
            },
            status_code=201
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )


# DELETE SLO by slo_code
async def delete_slo(db: AsyncSession, slo_code: str):
    try:
        result = await db.execute(select(Slo).where(Slo.slo_code == slo_code))
        slo = result.scalars().first()
        if not slo:
            return JSONResponse(
                {"statusCode": 404, "error": "SLO not found!"},
                status_code=404
            )

        await db.execute(
            SloTranslation.__table__.delete().where(SloTranslation.slo_code == slo_code)
        )

        await db.delete(slo)
        await db.commit()

        return JSONResponse(
            {"statusCode": 200, "message": "SLO and its translations deleted successfully!"},
            status_code=200
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )


# UPDATE SLO by slo_code
async def update_slo(db: AsyncSession, slo_code: str, slo_data):
    try:
        res = await db.execute(select(Slo).where(Slo.slo_code == slo_code))
        slo = res.scalars().first()
        if not slo:
            return JSONResponse(
                {"statusCode": 404, "error": "SLO not found!"},
                status_code=404
            )
        
        tr_res_az = await db.execute(
            select(SloTranslation).where(
                SloTranslation.slo_code == slo_code,
                SloTranslation.language_code == "az"
            )
        )
        tr_res_en = await db.execute(
            select(SloTranslation).where(
                SloTranslation.slo_code == slo_code,
                SloTranslation.language_code == "en"
            )
        )
        tr_az = tr_res_az.scalars().first()
        tr_en = tr_res_en.scalars().first()

        if not tr_az or not tr_en:
            return JSONResponse(
                {
                    "statusCode": 404,
                    "error": f"SLO translation not found!"
                },
                status_code=404
            )

        tr_az.slo_content = slo_data.slo_content
        tr_en.slo_content = translate_to_english(slo_data.slo_content)
        
        await db.commit()
        await db.refresh(slo)

        return JSONResponse(
            {
                "statusCode": 200,
                "message": f"SLO updated successfully."
            },
            status_code=200
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )