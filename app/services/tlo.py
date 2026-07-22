import logging
import traceback
from datetime import datetime
from app.models.tlo import Tlo
from app.models.topic import Topic
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.utils.code_generator import generate_code
from app.api.v1.schemas.tlo import CreateTlo
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translation.tlo_translation import TloTranslations

logger = logging.getLogger(__name__)


def generate_tlo_code():
    # Same 90k-space collision defect the topic codes had; a collision here
    # makes one TLO render another's text.
    return generate_code("TLO")


async def add_tlo(
    tlo_request: CreateTlo,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        topic_query = await db.execute(
            select(Topic).where(Topic.topic_code == tlo_request.topic_code)
        )
        topic = topic_query.scalars().first()

        if not topic:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Topic not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        tlo_code = generate_tlo_code()

        new_tlo = Tlo(
            subject_code=topic.subject_code,
            topic_code=topic.topic_code,
            tlo_code=tlo_code,
            created_at=datetime.utcnow()
        )

        new_tlo_az = TloTranslations(
            tlo_code=tlo_code,
            language_code="az",
            tlo_content=tlo_request.tlo_content,
            created_at=datetime.utcnow()
        )

        new_tlo_en = TloTranslations(
            tlo_code=tlo_code,
            language_code="en",
            tlo_content=translate_to_english(tlo_request.tlo_content),
            created_at=datetime.utcnow()
        )

        db.add(new_tlo)
        db.add(new_tlo_az)
        db.add(new_tlo_en)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "TLO added successfully.",
                "tlo_code": tlo_code
            }, status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        await db.rollback()
        logger.exception("Error in add_tlo")
        traceback.print_exc()
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def get_tlo_by_topic_code(
    topic_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        tlo_query = await db.execute(
            select(Tlo).where(Tlo.topic_code == topic_code)
        )
        tlos = tlo_query.scalars().all()

        tlos_arr = []
        for tlo in tlos:
            content_query = await db.execute(
                select(TloTranslations).where(
                    TloTranslations.tlo_code == tlo.tlo_code,
                    TloTranslations.language_code == lang_code
                )
            )
            translation = content_query.scalar_one_or_none()

            tlos_arr.append({
                "topic_code": tlo.topic_code,
                "tlo_code": tlo.tlo_code,
                "tlo_content": translation.tlo_content if translation else None,
            })

        return JSONResponse(
            content={
                "statusCode": 200,
                "tlos": tlos_arr
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        logger.exception("Error in get_tlo_by_topic_code")
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def update_tlo(
    tlo_request,
    db: AsyncSession = Depends(get_db)
):
    try:
        tlo_query = await db.execute(
            select(Tlo).where(Tlo.tlo_code == tlo_request.tlo_code)
        )
        tlo = tlo_query.scalars().first()

        if not tlo:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "TLO not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        az_query = await db.execute(
            select(TloTranslations).where(
                TloTranslations.tlo_code == tlo_request.tlo_code,
                TloTranslations.language_code == "az"
            )
        )
        az = az_query.scalar_one_or_none()

        en_query = await db.execute(
            select(TloTranslations).where(
                TloTranslations.tlo_code == tlo_request.tlo_code,
                TloTranslations.language_code == "en"
            )
        )
        en = en_query.scalar_one_or_none()

        if az is not None:
            az.tlo_content = tlo_request.tlo_content
            az.updated_at = datetime.utcnow()
        if en is not None:
            en.tlo_content = translate_to_english(tlo_request.tlo_content)
            en.updated_at = datetime.utcnow()

        tlo.updated_at = datetime.utcnow()
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "TLO updated successfully."
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        logger.exception("Error in update_tlo")
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def delete_tlo(
    tlo_code: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        tlo_query = await db.execute(
            select(Tlo).where(Tlo.tlo_code == tlo_code)
        )
        tlo = tlo_query.scalars().first()

        if not tlo:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "TLO not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        translations_query = await db.execute(
            select(TloTranslations).where(TloTranslations.tlo_code == tlo_code)
        )
        for translation in translations_query.scalars().all():
            await db.delete(translation)

        await db.delete(tlo)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "TLO deleted successfully."
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        logger.exception("Error in delete_tlo")
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
