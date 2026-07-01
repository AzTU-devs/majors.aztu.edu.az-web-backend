import logging
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clo import Clo
from app.models.clo_plo_match import CloPloMatch
from app.api.v1.schemas.clo_plo_match import CloPloMatchPayload

logger = logging.getLogger(__name__)


def _internal_error() -> JSONResponse:
    return JSONResponse(
        {"statusCode": 500, "message": "Internal server error"},
        status_code=500,
    )


async def toggle_clo_plo_match(payload: CloPloMatchPayload, db: AsyncSession):
    try:
        existing_q = await db.execute(
            select(CloPloMatch).where(
                CloPloMatch.clo_code == payload.clo_code,
                CloPloMatch.plo_code == payload.plo_code,
            )
        )
        existing = existing_q.scalars().first()

        if payload.match:
            if existing:
                return JSONResponse(
                    content={"statusCode": 200, "message": "Already matched."},
                    status_code=status.HTTP_200_OK,
                )
            row = CloPloMatch(
                clo_code=payload.clo_code,
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
        logger.exception("Error in toggle_clo_plo_match")
        return _internal_error()


async def get_clo_plo_matches_by_subject(subject_code: str, db: AsyncSession):
    """Return every clo→plo match for the CLOs that belong to a subject."""
    try:
        clo_rows = await db.execute(
            select(Clo.clo_code).where(Clo.subject_code == subject_code)
        )
        clo_codes = [c for (c,) in clo_rows.all()]

        if not clo_codes:
            return JSONResponse(
                content={"statusCode": 200, "data": []},
                status_code=status.HTTP_200_OK,
            )

        rows_q = await db.execute(
            select(CloPloMatch).where(CloPloMatch.clo_code.in_(clo_codes))
        )
        rows = rows_q.scalars().all()
        return JSONResponse(
            content={
                "statusCode": 200,
                "data": [
                    {"clo_code": r.clo_code, "plo_code": r.plo_code}
                    for r in rows
                ],
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error in get_clo_plo_matches_by_subject")
        return _internal_error()


async def get_clo_plo_matches_by_clo(clo_code: str, db: AsyncSession):
    try:
        rows_q = await db.execute(
            select(CloPloMatch).where(CloPloMatch.clo_code == clo_code)
        )
        rows = rows_q.scalars().all()
        return JSONResponse(
            content={
                "statusCode": 200,
                "data": [
                    {"clo_code": r.clo_code, "plo_code": r.plo_code}
                    for r in rows
                ],
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error in get_clo_plo_matches_by_clo")
        return _internal_error()
