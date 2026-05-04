import os
import requests
from datetime import datetime
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from app.models.faculty import Faculty
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translation.faculty_translations import FacultyTranslations


async def get_faculties_from_lms(db: AsyncSession = Depends(get_db)):
    api_url = os.getenv('LMS_API_FACULTIES')
    if not api_url:
        return JSONResponse(content={"error": "LMS_API_FACULTIES environment variable is not set."}, status_code=500)

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
        faculty_data = response.json()

        print("faculty_data:", faculty_data)

        if isinstance(faculty_data, dict) and "faculties" in faculty_data:
            faculty_list = faculty_data["faculties"]
        else:
            faculty_list = faculty_data

        validated_faculties = []
        for item in faculty_list:
            try:
                existing_faculty_result = await db.execute(
                    select(Faculty).where(Faculty.faculty_code == item["faculty_code"])
                )
                existing_faculty = existing_faculty_result.scalars().first()
                if not existing_faculty:
                    faculty_data_dict = {
                        "faculty_code": item["faculty_code"],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    faculty = Faculty(**faculty_data_dict)
                    db.add(faculty)
                else:
                    faculty = existing_faculty

                faculty_translation_az = FacultyTranslations(
                    faculty_code=faculty.faculty_code,
                    faculty_name=item["faculty_name"],
                    lang_code="az",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                faculty_translation_en = FacultyTranslations(
                    faculty_code=faculty.faculty_code,
                    faculty_name=translate_to_english(item["faculty_name"]),
                    lang_code="en",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(faculty_translation_az)
                db.add(faculty_translation_en)

                validated_faculties.append({
                    "faculty_code": faculty.faculty_code,
                    "faculty_name": faculty_translation_az.faculty_name,
                    "created_at": faculty.created_at.isoformat()
                })
            except Exception as e:
                print("Skipping item due to error:", e, item)

        await db.commit()

        if validated_faculties:
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "Faculties fetched successfully",
                    "faculties": validated_faculties
                }, status_code=status.HTTP_200_OK
        )
        
        else:
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "No faculties returned from LMS.",
                    "faculties": []
                }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
async def get_faculties(
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        fetched_data = await db.execute(
            select(FacultyTranslations)
            .where(FacultyTranslations.lang_code == lang_code)
        )

        faculties = fetched_data.scalars().all()

        if not faculties:
            return JSONResponse(
                content={
                    "status": 204,
                    "message": "No faculties found",
                    "faculties": []
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        return JSONResponse(
            content={
                "status": 200,
                "message": "Faculties fethed successfully.",
                "faculties": [
                    {
                        "faculty_code": faculty.faculty_code,
                        "faculty_name": faculty.faculty_name
                    } for faculty in faculties
                ]
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )