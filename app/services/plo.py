import random
import sqlalchemy as sa
from app.models.plo import Plo
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.models.speciality import Specialty
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translation.plo_translations import PloTranslation

allowed_languages = ["en","az"]

def generate_plo_code():
    random_number = random.randint(10000, 99999)
    return f"PLO-{random_number}"

async def get_all_plos(db: AsyncSession, lang: str = Depends(get_language)):
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
            select(Plo, PloTranslation)
            .join(PloTranslation, Plo.plo_code == PloTranslation.plo_code)
            .where(PloTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": f"No PLO found for language '{lang}'!"
                },
                status_code=204
            )

        plos = []
        for plo, translation in rows:
            plos.append({
                "id": plo.id,
                "specialty_code": plo.specialty_code,
                "plo_code": plo.plo_code,
                "language_code": translation.language_code,
                "plo_content": translation.plo_content
            })

        return JSONResponse(
            content={
                "statusCode": 200,
                "message":  f"All PLOs fetched successfully for language '{lang}'!",
                "plos": plos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )


# GET by specialty_code
async def get_plos_by_specialty(
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
            select(Plo, PloTranslation)
            .join(PloTranslation, Plo.plo_code == PloTranslation.plo_code)
            .where(Plo.specialty_code == specialty_code)
            .where(PloTranslation.language_code == lang)
        )

        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No PLO found for this specialty!",
                },
                status_code=204
            )

        plos = []
        for plo, translation in rows:
            plos.append({
                "id": plo.id,
                "specialty_code": plo.specialty_code,
                "plo_code": plo.plo_code,
                "language_code": translation.language_code,
                "plo_content": translation.plo_content
            })

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "PLOs fetched successfully!",
                "plos": plos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )

# Create PLO with translations
async def create_plo(db: AsyncSession, plo_data):
    try:
        specialty_q = await db.execute(
            select(Specialty).where(Specialty.specialty_code == plo_data.specialty_code)
        )
        if not specialty_q.scalars().first():
            return JSONResponse(
                content={"statusCode": 404, "message": "Specialty code does not exist!"},
                status_code=404
            )
        
        plo_code = generate_plo_code()

        new_plo = Plo(
            specialty_code=plo_data.specialty_code,
            plo_code=plo_code,
        )
        db.add(new_plo)

        new_translation_az = PloTranslation(
            plo_code=plo_code,
            language_code="az",
            plo_content=plo_data.plo_content,
        )

        new_translation_en = PloTranslation(
            plo_code=plo_code,
            language_code="en",
            plo_content=translate_to_english(plo_data.plo_content),
        )

        db.add(new_translation_az)
        db.add(new_translation_en)

        await db.commit()
        return JSONResponse(
            content={
                "statusCode": 201,
                "message": f"PLO created successfully with translation."
            },
            status_code=201
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )

# DELETE PLO by plo_code
async def delete_plo(db: AsyncSession, plo_code: str):
    try:
        result = await db.execute(select(Plo).where(Plo.plo_code == plo_code))
        plo = result.scalars().first()
        if not plo:
            return JSONResponse(
                {"statusCode": 404, "error": "PLO not found!"},
                status_code=404
            )

        await db.execute(
            PloTranslation.__table__.delete().where(PloTranslation.plo_code == plo_code)
        )

        await db.delete(plo)
        await db.commit()

        return JSONResponse(
            {"statusCode": 200, "message": "PLO and its translations deleted successfully!"},
            status_code=200
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )

# UPDATE PLO by plo_code
async def update_plo(db: AsyncSession, plo_code: str, plo_data):
    try:
        res = await db.execute(select(Plo).where(Plo.plo_code == plo_code))
        plo = res.scalars().first()
        if not plo:
            return JSONResponse(
                {"statusCode": 404, "error": "PLO not found!"},
                status_code=404
            )
        
        tr_res_az = await db.execute(
            select(PloTranslation).where(
                PloTranslation.plo_code == plo_code,
                PloTranslation.language_code == "az"
            )
        )
        tr_res_en = await db.execute(
            select(PloTranslation).where(
                PloTranslation.plo_code == plo_code,
                PloTranslation.language_code == "en"
            )
        )
        tr_az = tr_res_az.scalars().first()
        tr_en = tr_res_en.scalars().first()

        if not tr_az or not tr_en:
            return JSONResponse(
                {
                    "statusCode": 404,
                    "error": f"PLO translation not found for language."
                },
                status_code=404
            )

        tr_az.plo_content = plo_data.plo_content
        tr_en.plo_content = translate_to_english(plo_data.plo_content)

        await db.commit()
        await db.refresh(plo)

        return JSONResponse(
            {
                "statusCode": 200,
                "message": f"PLO updated successfully for language!"
            },
            status_code=200
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )