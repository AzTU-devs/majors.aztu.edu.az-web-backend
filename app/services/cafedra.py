import os
import logging
import requests
from datetime import datetime
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.faculty import Faculty
from app.models.cafedra import Cafedra
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.api.v1.schemas.cafedra import CreateCafedraManual
from app.models.translation.cafedra_translations import CafedraTranslations

logger = logging.getLogger(__name__)


async def add_cafedra_manual(
    payload: CreateCafedraManual,
    db: AsyncSession,
):
    try:
        faculty_query = await db.execute(
            select(Faculty).where(Faculty.faculty_code == payload.faculty_code)
        )
        if not faculty_query.scalars().first():
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Faculty not found.",
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        existing = await db.execute(
            select(Cafedra).where(Cafedra.cafedra_code == payload.cafedra_code)
        )
        if existing.scalars().first():
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "Cafedra code already exists.",
                },
                status_code=status.HTTP_409_CONFLICT,
            )

        now = datetime.utcnow()
        cafedra = Cafedra(
            faculty_code=payload.faculty_code,
            cafedra_code=payload.cafedra_code,
            created_at=now,
            updated_at=now,
        )
        db.add(cafedra)

        translation_az = CafedraTranslations(
            cafedra_code=payload.cafedra_code,
            lang_code="az",
            cafedra_name=payload.cafedra_name,
            created_at=now,
            updated_at=now,
        )
        translation_en = CafedraTranslations(
            cafedra_code=payload.cafedra_code,
            lang_code="en",
            cafedra_name=translate_to_english(payload.cafedra_name),
            created_at=now,
            updated_at=now,
        )
        db.add(translation_az)
        db.add(translation_en)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "Cafedra code already exists.",
                },
                status_code=status.HTTP_409_CONFLICT,
            )

        await db.refresh(cafedra)
        await db.refresh(translation_az)
        await db.refresh(translation_en)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "Cafedra created successfully.",
                "cafedra": {
                    "id": cafedra.id,
                    "faculty_code": cafedra.faculty_code,
                    "cafedra_code": cafedra.cafedra_code,
                    "cafedra_name": translation_az.cafedra_name,
                },
            },
            status_code=status.HTTP_201_CREATED,
        )

    except Exception:
        logger.exception("Error in add_cafedra_manual")
        return JSONResponse(
            content={"statusCode": 500, "message": "Internal server error"},
            status_code=500,
        )


async def get_cafedras_from_lms(db: AsyncSession = Depends(get_db)):
    api_url = os.getenv('LMS_API_CAFEDRAS')
    if not api_url:
        return JSONResponse(content={"error": "LMS_API_CAFEDRAS environment variable is not set."}, status_code=500)

    api_key = os.getenv('API_KEY')
    if not api_key:
        return JSONResponse(content={"error": "API_KEY environment variable is not set."}, status_code=500)

    headers = {
        'x-api-key': api_key,
        'Accept': 'application/json'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        cafedra_data = response.json()

        if isinstance(cafedra_data, dict) and "cafedras" in cafedra_data:
            cafedra_list = cafedra_data["cafedras"]
        else:
            cafedra_list = cafedra_data

        validated_cafedras = []
        for item in cafedra_list:
            try:
                existing_cafedra_result = await db.execute(
                    select(Cafedra).where(Cafedra.cafedra_code == item["cafedra_code"])
                )
                existing_cafedra = existing_cafedra_result.scalars().first()

                if not existing_cafedra:
                    cafedra_obj = Cafedra(
                        faculty_code=item["faculty_code"],
                        cafedra_code=item["cafedra_code"],
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(cafedra_obj)
                    await db.flush()
                else:
                    cafedra_obj = existing_cafedra

                cafedra_translation_az = CafedraTranslations(
                    cafedra_code=cafedra_obj.cafedra_code,
                    cafedra_name=item["cafedra_name"],
                    lang_code="az",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                cafedra_translation_en = CafedraTranslations(
                    cafedra_code=cafedra_obj.cafedra_code,
                    cafedra_name=translate_to_english(item["cafedra_name"]),
                    lang_code="en",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                db.add(cafedra_translation_az)
                db.add(cafedra_translation_en)

                validated_cafedras.append({
                    "faculty_code": cafedra_obj.faculty_code,
                    "cafedra_code": cafedra_obj.cafedra_code,
                    "cafedra_name": cafedra_translation_az.cafedra_name,
                    "created_at": cafedra_obj.created_at.isoformat()
                })

            except Exception as e:
                print("Skipping item due to error:", e, item)

        await db.commit()

        if validated_cafedras:
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "Cafedras fetched successfully",
                    "cafedras": validated_cafedras
                }, status_code=status.HTTP_200_OK
            )
        else:
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "No cafedras returned from LMS.",
                    "cafedras": []
                }, status_code=status.HTTP_200_OK
            )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_cafedras(
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        fetched_data = await db.execute(
            select(Cafedra, CafedraTranslations)
            .join(
                CafedraTranslations,
                CafedraTranslations.cafedra_code == Cafedra.cafedra_code,
            )
            .where(CafedraTranslations.lang_code == lang_code)
        )
        rows = fetched_data.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "No cafedra found.",
                    "cafedras": []
                }, status_code=200
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Cafedras fetched successfully.",
                "cafedras" : [
                    {
                        "faculty_code": cafedra.faculty_code,
                        "cafedra_code": cafedra.cafedra_code,
                        "cafedra_name": translation.cafedra_name,
                        "created_at": str(cafedra.created_at) if cafedra.created_at else None,
                        "updated_at": str(cafedra.updated_at) if cafedra.updated_at else None
                    } for cafedra, translation in rows
                ]
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }
        )

async def get_cafedra_by_faculty(
    faculty_code: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        faculty_query = await db.execute(
            select(Faculty)
            .where(Faculty.faculty_code == faculty_code)
        )

        faculty = faculty_query.scalar_one_or_none()

        if not faculty:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Faculty code is not valid."
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        cafedra_query = await db.execute(
            select(Cafedra)
            .where(Cafedra.faculty_code == faculty_code)
        )
        
        cafedras = cafedra_query.scalars().all()

        cafedra_details_arr = []

        for cafedra in cafedras:
            cafedra_details_query = await db.execute(
                select(CafedraTranslations)
                .where(
                    CafedraTranslations.cafedra_code == cafedra.cafedra_code,
                    CafedraTranslations.lang_code == lang_code
                )
            )

            cafedra_details = cafedra_details_query.scalar_one_or_none()

            cafedra_obj = {
                "id": cafedra.id,
                "cafedra_code": cafedra.cafedra_code,
                "cafedra_name": cafedra_details.cafedra_name
            }

            cafedra_details_arr.append(cafedra_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Cafedras fetched successfully.",
                "cafedras": cafedra_details_arr
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }
        )