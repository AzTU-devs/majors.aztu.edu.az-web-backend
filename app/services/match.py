import logging
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subject_plo_match import SubjectPloMatch
from app.api.v1.schemas.match import MatchPayload

logger = logging.getLogger(__name__)


def _internal_error() -> JSONResponse:
    return JSONResponse(
        {"statusCode": 500, "message": "Internal server error"},
        status_code=500,
    )


async def toggle_match(payload: MatchPayload, db: AsyncSession):
    try:
        existing_q = await db.execute(
            select(SubjectPloMatch).where(
                SubjectPloMatch.subject_code == payload.subject_code,
                SubjectPloMatch.plo_code == payload.plo_code,
            )
        )
        existing = existing_q.scalars().first()

        if payload.match:
            if existing:
                return JSONResponse(
                    content={"statusCode": 200, "message": "Already matched."},
                    status_code=status.HTTP_200_OK,
                )
            row = SubjectPloMatch(
                subject_code=payload.subject_code,
                plo_code=payload.plo_code,
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
        logger.exception("Error in toggle_match")
        return _internal_error()


async def get_matches_by_subject(subject_code: str, db: AsyncSession):
    try:
        rows_q = await db.execute(
            select(SubjectPloMatch).where(
                SubjectPloMatch.subject_code == subject_code
            )
        )
        rows = rows_q.scalars().all()
        return JSONResponse(
            content={
                "statusCode": 200,
                "data": [
                    {"subject_code": r.subject_code, "plo_code": r.plo_code}
                    for r in rows
                ],
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error in get_matches_by_subject")
        return _internal_error()
