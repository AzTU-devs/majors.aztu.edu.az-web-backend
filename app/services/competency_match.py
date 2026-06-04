import logging
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subject_competency_match import SubjectCompetencyMatch
from app.api.v1.schemas.competency_match import CompetencyMatchPayload

logger = logging.getLogger(__name__)


def _internal_error() -> JSONResponse:
    return JSONResponse(
        {"statusCode": 500, "message": "Internal server error"},
        status_code=500,
    )


async def toggle_competency_match(payload: CompetencyMatchPayload, db: AsyncSession):
    try:
        existing_q = await db.execute(
            select(SubjectCompetencyMatch).where(
                SubjectCompetencyMatch.subject_code == payload.subject_code,
                SubjectCompetencyMatch.competency_code == payload.competency_code,
            )
        )
        existing = existing_q.scalars().first()

        if payload.match:
            if existing:
                return JSONResponse(
                    content={"statusCode": 200, "message": "Already matched."},
                    status_code=status.HTTP_200_OK,
                )
            row = SubjectCompetencyMatch(
                subject_code=payload.subject_code,
                competency_code=payload.competency_code,
                created_at=datetime.utcnow(),
            )
            db.add(row)
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
            return JSONResponse(
                content={"statusCode": 201, "message": "Match created."},
                status_code=status.HTTP_201_CREATED,
            )

        # match=False → remove if exists
        if existing:
            await db.delete(existing)
            await db.commit()
        return JSONResponse(
            content={"statusCode": 200, "message": "Match removed."},
            status_code=status.HTTP_200_OK,
        )

    except Exception:
        logger.exception("Error in toggle_competency_match")
        return _internal_error()


async def get_matches_by_competency(competency_code: str, db: AsyncSession):
    try:
        rows_q = await db.execute(
            select(SubjectCompetencyMatch).where(
                SubjectCompetencyMatch.competency_code == competency_code
            )
        )
        rows = rows_q.scalars().all()
        return JSONResponse(
            content={
                "statusCode": 200,
                "data": [
                    {"subject_code": r.subject_code, "competency_code": r.competency_code}
                    for r in rows
                ],
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error in get_matches_by_competency")
        return _internal_error()


async def get_matches_by_subject(subject_code: str, db: AsyncSession):
    try:
        rows_q = await db.execute(
            select(SubjectCompetencyMatch).where(
                SubjectCompetencyMatch.subject_code == subject_code
            )
        )
        rows = rows_q.scalars().all()
        return JSONResponse(
            content={
                "statusCode": 200,
                "data": [
                    {"subject_code": r.subject_code, "competency_code": r.competency_code}
                    for r in rows
                ],
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error in get_matches_by_subject")
        return _internal_error()
