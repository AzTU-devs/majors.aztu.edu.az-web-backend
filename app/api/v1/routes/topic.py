from app.services.topic import *
from app.db.session import get_db
from app.utils.language import get_language
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.topic import CreateTopic, UpdateTopic
from app.utils.jwt import token_required

router = APIRouter()

@router.post("/topic/create", dependencies=[Depends(token_required())])
async def create_topic(
    topic_request: CreateTopic,
    db: AsyncSession = Depends(get_db)
):
    return await add_topic(topic_request, db)

@router.patch("/topic/update", dependencies=[Depends(token_required())])
async def update_topic_endpoint(
    topic_request: UpdateTopic,
    db: AsyncSession = Depends(get_db)
):
    return await update_topic(topic_request, db)

@router.get("/topic/{subject_code}")
async def get_topics(
    subject_code: str,
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=1),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_topic_by_subject_code(subject_code, start, end, lang_code, db)