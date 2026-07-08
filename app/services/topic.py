import random
from datetime import datetime
from app.models.clo import Clo
from app.db.session import get_db
from app.models.topic import Topic
from sqlalchemy.future import select
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.topic import CreateTopic
from app.utils.translator import translate_to_english
from app.models.curricula_program import CurriculaProgram
from app.models.translation.topic_translations import TopicTranslations
from app.models.tlo import Tlo
from app.models.translation.tlo_translation import TloTranslations
from sqlalchemy import func
import traceback

def generate_topic_code():
    random_number = random.randint(10000, 99999)
    return f"PLO-{random_number}"

async def add_topic(
    topic_request: CreateTopic,
    db: AsyncSession = Depends(get_db)
):
    try:
        subject_query = await db.execute(
            select(CurriculaProgram)
            .where(CurriculaProgram.subject_code == topic_request.subject_code)
        )

        subject = subject_query.scalars().first()

        if not subject:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Subject not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        topic_code = generate_topic_code()
        
        new_topic = Topic(
            subject_code=topic_request.subject_code,
            topic_code=topic_code,
            topic_url=topic_request.topic_url,
            topic_type=topic_request.topic_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        new_topic_az = TopicTranslations(
            topic_code=topic_code,
            language_code="az",
            topic_name=topic_request.topic_name,
            topic_result=topic_request.topic_result,
            topic_description=topic_request.topic_desc,
            created_at=datetime.utcnow()
        )

        new_topic_en = TopicTranslations(
            topic_code=topic_code,
            topic_name=translate_to_english(topic_request.topic_name),
            topic_description=translate_to_english(topic_request.topic_desc),
            topic_result=translate_to_english(topic_request.topic_result),
            language_code="en",
            created_at=datetime.utcnow()
        )

        db.add(new_topic)
        db.add(new_topic_az)
        db.add(new_topic_en)
        await db.commit()
        await db.refresh(new_topic)
        await db.refresh(new_topic_az)
        await db.refresh(new_topic_en)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "Topic created successfully."
            }, status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        print("Add topic error:", e)
        traceback.print_exc()
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def update_topic(
    topic_request,
    db: AsyncSession = Depends(get_db)
):
    try:
        topic_query = await db.execute(
            select(Topic).where(Topic.topic_code == topic_request.topic_code)
        )
        topic = topic_query.scalars().first()

        if not topic:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Topic not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        # Update the language-independent fields on the topic itself.
        if topic_request.topic_url is not None:
            topic.topic_url = topic_request.topic_url
        if topic_request.topic_type is not None:
            topic.topic_type = topic_request.topic_type
        topic.updated_at = datetime.utcnow()

        # Update the Azerbaijani translation (source of truth) and mirror the
        # changed text fields to English via the translator.
        az_query = await db.execute(
            select(TopicTranslations).where(
                TopicTranslations.topic_code == topic_request.topic_code,
                TopicTranslations.language_code == "az"
            )
        )
        az = az_query.scalar_one_or_none()

        en_query = await db.execute(
            select(TopicTranslations).where(
                TopicTranslations.topic_code == topic_request.topic_code,
                TopicTranslations.language_code == "en"
            )
        )
        en = en_query.scalar_one_or_none()

        if az is not None:
            if topic_request.topic_name is not None:
                az.topic_name = topic_request.topic_name
                if en is not None:
                    en.topic_name = translate_to_english(topic_request.topic_name)
            if topic_request.topic_desc is not None:
                az.topic_description = topic_request.topic_desc
                if en is not None:
                    en.topic_description = translate_to_english(topic_request.topic_desc)
            if topic_request.topic_result is not None:
                az.topic_result = topic_request.topic_result
                if en is not None:
                    en.topic_result = translate_to_english(topic_request.topic_result)
            az.updated_at = datetime.utcnow()
            if en is not None:
                en.updated_at = datetime.utcnow()

        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Topic updated successfully."
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        print("Update topic error:", e)
        traceback.print_exc()
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_topic_by_subject_code(
    subject_code: str,
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=1),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        subject_query = await db.execute(
            select(CurriculaProgram)
            .where(CurriculaProgram.subject_code == subject_code)
        )

        subject = subject_query.scalars().first()

        if not subject:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Subject not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        total_query = await db.execute(
            select(func.count()).select_from(Topic).where(Topic.subject_code == subject_code)
        )
        total = total_query.scalar()

        topic_arr = []

        topic_query = await db.execute(
            select(Topic)
            .where(Topic.subject_code == subject_code)
            .order_by(Topic.id)
            .offset(start)
            .limit(end - start)
        )

        topics = topic_query.scalars().all()

        if not topics:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No content"
                }, status_code=status.HTTP_200_OK
            )

        for topic in topics:
            topic_translations_query = await db.execute(
                select(TopicTranslations)
                .where(
                    TopicTranslations.topic_code == topic.topic_code,
                    TopicTranslations.language_code == lang_code
                )
            )

            topic_translations = topic_translations_query.scalar_one_or_none()

            topic_obj = {
                "topic_code": topic.topic_code,
                "topic_name": topic_translations.topic_name,
                "topic_url": topic.topic_url,
                "topic_desc": topic_translations.topic_description,
                "topic_type": topic.topic_type,
                "topic_result": topic_translations.topic_result,
                "created_at": topic.created_at.isoformat() if topic.created_at else None
            }

            topic_arr.append(topic_obj)
        
        return JSONResponse(
            content={
                "statusCode": 200,
                "topics": topic_arr,
                "total": total
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def delete_topic(
    topic_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a topic and everything under it (its translations and its TLOs)."""
    try:
        topic_query = await db.execute(select(Topic).where(Topic.topic_code == topic_code))
        topic = topic_query.scalars().first()
        if not topic:
            return JSONResponse(
                content={"statusCode": 404, "message": "Topic not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # TLOs (topic learning outcomes) under this topic + their translations.
        tlo_rows = await db.execute(select(Tlo).where(Tlo.topic_code == topic_code))
        tlos = tlo_rows.scalars().all()
        tlo_codes = [t.tlo_code for t in tlos]
        if tlo_codes:
            tlo_tr = await db.execute(
                select(TloTranslations).where(TloTranslations.tlo_code.in_(tlo_codes))
            )
            for tr in tlo_tr.scalars().all():
                await db.delete(tr)
        for t in tlos:
            await db.delete(t)

        # Topic translations.
        topic_tr = await db.execute(
            select(TopicTranslations).where(TopicTranslations.topic_code == topic_code)
        )
        for tr in topic_tr.scalars().all():
            await db.delete(tr)

        await db.delete(topic)
        await db.commit()

        return JSONResponse(
            content={"statusCode": 200, "message": "Topic deleted successfully."},
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        await db.rollback()
        return JSONResponse(
            content={"statusCode": 500, "message": "Internal server error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )