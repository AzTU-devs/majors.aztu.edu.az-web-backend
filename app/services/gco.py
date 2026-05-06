import random
from fastapi import Depends
from app.models.gco import GCO
from app.db.session import get_db
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.models.speciality import Specialty
from app.api.v1.schemas.gco import GCOCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translation.gco_translations import GCOTranslation

def generate_gco_code():
    random_number = random.randint(10000, 99999)
    return f"GCO-{random_number}"

# GET All GCOs
async def get_all_gcos(db: AsyncSession, lang: str = Depends(get_language)):
    try:
        result = await db.execute(
            select(GCO, GCOTranslation)
            .join(GCOTranslation, GCO.career_code == GCOTranslation.career_code)
            .where(GCOTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": f"No GCO found for language '{lang}!'"
                },
                status_code=200
            )

        gcos = []
        for gco, translation in rows:
            gcos.append(
                {
                    "id": gco.id,
                    "specialty_code": gco.specialty_code,
                    "career_code": gco.career_code,
                    "language_code": translation.language_code,
                    "career_content": translation.career_content
                }
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": f"All GCOs fetched successfully for language '{lang}'!",
                "gcos": gcos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            },
            status_code=500
        )

# GET GCOs by specialty_code
async def get_gcos_by_specialty(specialty_code: str, lang: str, db: AsyncSession):
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
            select(GCO, GCOTranslation)
            .join(GCOTranslation, GCO.career_code == GCOTranslation.career_code)
            .where(GCO.specialty_code == specialty_code)
            .where(GCOTranslation.language_code == lang)
        )
        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No GCO found for this specialty in the requested language!",
                },
                status_code=200
            )

        gcos = []
        for gco, translation in rows:
            gcos.append(
                {
                    "id": gco.id,
                    "specialty_code": gco.specialty_code,
                    "career_code": gco.career_code,
                    "career_title": translation.career_title,
                    "language_code": translation.language_code,
                    "career_content": translation.career_content
                }
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "GCOs fetched successfully!",
                "gcos": gcos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            },
            status_code=500
        )

# CREATE GCO
async def create_gco(db: AsyncSession, gco_data: GCOCreate):
    try:
        specialty_q = await db.execute(
            select(Specialty).where(Specialty.specialty_code == gco_data.specialty_code)
        )

        if not specialty_q.scalars().first():
            return JSONResponse(
                content={"statusCode": 404, "message": "Specialty code does not exist!"},
                status_code=404
            )
        
        career_code = generate_gco_code()

        new_gco = GCO(
            specialty_code=gco_data.specialty_code,
            career_code=career_code
        )
        db.add(new_gco)

        new_translation_az = GCOTranslation(
            career_code=career_code,
            language_code="az",
            career_title=gco_data.career_title,
            career_content=gco_data.career_content
        )
        new_translation_en = GCOTranslation(
            career_code=career_code,
            language_code="en",
            career_title=translate_to_english(gco_data.career_title),
            career_content=translate_to_english(gco_data.career_content)
        )
        db.add(new_translation_az)
        db.add(new_translation_en)

        await db.commit()
        return JSONResponse(
            content={
                "statusCode": 201,
                "message": f"GCO created successfully with translation!"
            },
            status_code=201
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )

# DELETE GCO
async def delete_gco(db: AsyncSession, career_code: str):
    try:
        result = await db.execute(
            select(GCO).where(GCO.career_code == career_code)
        )
        gco = result.scalars().first()
        if not gco:
            return JSONResponse(
                {"statusCode": 404, "error": "GCO not found!"},
                status_code=404,
            )

        await db.execute(
            GCOTranslation.__table__.delete().where(
                GCOTranslation.career_code == career_code
            )
        )

        await db.delete(gco)
        await db.commit()

        return JSONResponse(
            {
                "statusCode": 200,
                "message": "GCO and its translations deleted successfully!",
            },
            status_code=200,
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500,
        )

# UPDATE GCO
async def update_gco(db: AsyncSession, career_code: str, gco_data):
    try:
        res = await db.execute(
            select(GCO).where(GCO.career_code == career_code)
        )
        gco = res.scalar_one_or_none()

        if not gco:
            return JSONResponse(
                {"statusCode": 404, "error": "GCO not found!"},
                status_code=404,
            )

        tr_res_az = await db.execute(
            select(GCOTranslation).where(
                GCOTranslation.career_code == career_code,
                GCOTranslation.language_code == "az",
            )
        )
        tr_res_en = await db.execute(
            select(GCOTranslation).where(
                GCOTranslation.career_code == career_code,
                GCOTranslation.language_code == "en",
            )
        )
        tr_az = tr_res_az.scalar_one_or_none()
        tr_en = tr_res_en.scalar_one_or_none()

        if not tr_az or not tr_en:
            return JSONResponse(
                {
                    "statusCode": 404,
                    "error": f"GCO translation does not exist!"
                },
                status_code=404,
            )
        
        tr_az.career_content=gco_data.career_content
        tr_en.career_content=translate_to_english(gco_data.career_content)

        await db.commit()
        await db.refresh(gco)

        return JSONResponse(
            {
                "statusCode": 200,
                "message": f"GCO updated successfully.",
            },
            status_code=200,
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )