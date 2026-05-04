from datetime import datetime
from app.db.session import get_db
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.models.university import University
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.api.v1.schemas.university import CreateUniversity

# Get all universities only by dev role

async def get_universities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(University))
    universities = result.scalars().all()

    if not universities:
        return {
            "statusCode": 200,
            "message": "No university found.",
            "universities": []
        }

    return {
        "statusCode": 200,
        "message": "Universities fetched successfully.",
        "universities": [
            {
                "university_code": u.university_code,
                "university_name": u.university_name,
                "university_short_name": u.university_short_name,
                "is_frozen": u.is_frozen,
                "frozen_at": str(u.frozen_at) if u.frozen_at else None,
                "created_at": str(u.created_at),
                "updated_at": str(u.updated_at),
                "deleted_at": str(u.deleted_at) if u.deleted_at else None
            }
            for u in universities
        ],
    }

# Get a single university by university_code only by dev role

async def get_university(
    university_code: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(University).where(University.university_code == university_code)
    )
    university = result.scalars().first()

    if not university:
        return JSONResponse(
            content={
                "statusCode": 404,
                "message": "Not found"
            },
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return {
        "statusCode": 200,
        "message": "University fetched successfully.",
        "university": {
            "id": university.id,
            "university_code": university.university_code,
            "university_name": university.university_name,
            "university_short_name": university.university_short_name,
            "is_frozen": university.is_frozen,
            "created_at": str(university.created_at),
            "updated_at": str(university.updated_at),
            "deleted_at": str(university.deleted_at) if university.deleted_at else None
        }
    }

# Add a new university only by dev role

async def add_university(
    university_details: CreateUniversity,
    db: AsyncSession = Depends(get_db) 
):
    result = await db.execute(
        select(University)
        .where(University.university_name == university_details.university_name)
    )
    exist_university = result.scalars().first()

    if exist_university:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="University already exists."
        )

    new_university = University(
        university_code=university_details.university_short_name,
        university_name=university_details.university_name,
        university_short_name=university_details.university_short_name,
        is_frozen=False,
        frozen_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        deleted_at=datetime.utcnow()
    )

    db.add(new_university)
    await db.commit()
    await db.refresh(new_university)

    return JSONResponse(
        content={
            "statusCode": 201,
            "message": "University created successfully."
        },
        status_code=status.HTTP_201_CREATED
    )

# Delete a university by university_code only by dev role

async def delete_university(
    university_code: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(University).where(University.university_code == university_code)
    )
    university = result.scalars().first()

    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found."
        )
    
    await db.delete(university)
    await db.commit()

    return JSONResponse(
        content={
            "statusCode": 200,
            "message": "University deleted successfully."
        },
        status_code=status.HTTP_200_OK
    )
