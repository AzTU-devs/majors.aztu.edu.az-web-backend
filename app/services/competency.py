import random
import sqlalchemy as sa
from fastapi import Depends
from app.db.session import get_db
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.models.speciality import Specialty
from app.models.competency import Competency
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.api.v1.schemas.competency import CompetencyCreate
from app.models.translation.competency_tranlation import CompetencyTranslation

allowed_languages = ["en", "az"]

def generate_competency_code():
    random_number = random.randint(10000, 99999)
    return f"COMPETENCY-{random_number}"


async def get_all_competency(db: AsyncSession, lang: str = Depends(get_language)):
    if lang not in allowed_languages:
        return JSONResponse(content={
            "statusCode": 404,
            "message": "Invalid language code!"
        }, 
        status_code=404
    )

    try:
        result = await db.execute(
            select(Competency, CompetencyTranslation)
            .join(CompetencyTranslation, Competency.competency_code == CompetencyTranslation.competency_code)
            .where(CompetencyTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": f"No competency found for language '{lang}!'"
                },
                status_code=204
            )

        competencies = []
        for competency, translation in rows:
            competencies.append(
                {
                    "id": competency.id,
                    "specialty_code": competency.specialty_code,
                    "competency_code": competency.competency_code,
                    "language_code": translation.language_code,
                    "competency_content": translation.competency_content
                }
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": f"All competencies fetched successfully for language '{lang}'!",
                "competencies": competencies
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

# GET Competencies by specialty_code
async def get_competencies_by_specialty(specialty_code: str, lang: str, db: AsyncSession):
    if lang not in allowed_languages:
        return JSONResponse(
            content={
                "statusCode": 404,
                "message": "Invalid language code!"
            },
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
            select(Competency, CompetencyTranslation)
            .join(CompetencyTranslation, Competency.competency_code == CompetencyTranslation.competency_code)
            .where(Competency.specialty_code == specialty_code)
            .where(CompetencyTranslation.language_code == lang)
        )
        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No competency found for this specialty in the requested language!",
                },
                status_code=204
            )

        competencies = []
        for competency, translation in rows:
            competencies.append(
                {
                    "id": competency.id,
                    "specialty_code": competency.specialty_code,
                    "competency_code": competency.competency_code,
                    "language_code": translation.language_code,
                    "competency_content": translation.competency_content
                }
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Competencies fetched successfully!",
                "competencies": competencies
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

# CREATE Competency
async def create_competency(db: AsyncSession, competency_data: CompetencyCreate):
    try:
        specialty_q = await db.execute(
            select(Specialty).where(Specialty.specialty_code == competency_data.specialty_code)
        )

        if not specialty_q.scalars().first():
            return JSONResponse(
                content={"statusCode": 404, "message": "Specialty code does not exist!"},
                status_code=404
            )
        
        competency_code = generate_competency_code()

        new_competency = Competency(
            specialty_code=competency_data.specialty_code,
            competency_code=competency_code
        )
        db.add(new_competency)

        new_translation_az = CompetencyTranslation(
            competency_code=competency_code,
            language_code='az',
            competency_content=competency_data.competency_content
        )

        new_translation_en = CompetencyTranslation(
            competency_code=competency_code,
            language_code='en',
            competency_content=translate_to_english(competency_data.competency_content)
        )
        db.add(new_translation_az)
        db.add(new_translation_en)

        await db.commit()
        await db.refresh(new_translation_az)
        await db.refresh(new_translation_en)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": f"Competency created successfully with translation!"
            },
            status_code=201
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )

# DELETE Competency
async def delete_competency(db: AsyncSession, competency_code: str):
    try:
        result = await db.execute(
            select(Competency).where(Competency.competency_code == competency_code)
        )
        competency = result.scalars().first()
        if not competency:
            return JSONResponse(
                {"statusCode": 404, "error": "Competency not found!"},
                status_code=404,
            )

        await db.execute(
            CompetencyTranslation.__table__.delete().where(
                CompetencyTranslation.competency_code == competency_code
            )
        )

        await db.delete(competency)
        await db.commit()

        return JSONResponse(
            {
                "statusCode": 200,
                "message": "Competency and its translations deleted successfully!",
            },
            status_code=200,
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500,
        )

# UPDATE Competency
async def update_competency(
    db: AsyncSession,
    competency_code: str,
    competency_data
):
    try:
        res = await db.execute(
            select(Competency)
            .where(Competency.competency_code == competency_code)
        )

        competency = res.scalars().first()

        if not competency:
            return JSONResponse(
                {"statusCode": 404, "error": "Competency not found!"},
                status_code=404,
            )
        
        tr_res_az = await db.execute(
            select(CompetencyTranslation).where(
                CompetencyTranslation.competency_code == competency_code,
                CompetencyTranslation.language_code == 'az'
            )
        )

        tr_res_en = await db.execute(
            select(CompetencyTranslation).where(
                CompetencyTranslation.competency_code == competency_code,
                CompetencyTranslation.language_code == 'en'
            )
        )

        tr_az = tr_res_az.scalars().first()
        tr_en = tr_res_en.scalars().first()

        if not tr_az or not tr_en:
            return JSONResponse(
                {
                    "statusCode": 404,
                    "error": f"Competency translation for language does not exist!"
                },
                status_code=404,
            )
        
        tr_az.competency_content = competency_data.competency_content
        tr_en.competency_content = translate_to_english(competency_data.competency_content)

        await db.commit()
        await db.refresh(competency)

        return JSONResponse(
            {
                "statusCode": 200,
                "message": f"Competency updated successfully for language!",
            },
            status_code=200,
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )