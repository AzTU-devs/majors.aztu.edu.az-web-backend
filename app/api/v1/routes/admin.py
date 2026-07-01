from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.utils.jwt import token_required
from app.api.v1.schemas.admin import CreateAdmin, UpdateAdmin
from app.services.admin import (
    create_admin,
    list_admins,
    get_admin,
    update_admin,
    delete_admin,
)

router = APIRouter()

# Only the admin / dev role (1) may manage admin profiles.
ADMIN_ONLY = Depends(token_required(allowed_roles=[1]))


@router.post("/admins", dependencies=[ADMIN_ONLY])
async def create_admin_endpoint(
    payload: CreateAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await create_admin(payload, db)


@router.get("/admins", dependencies=[ADMIN_ONLY])
async def list_admins_endpoint(
    db: AsyncSession = Depends(get_db),
):
    return await list_admins(db)


@router.get("/admins/{fin_kod}", dependencies=[ADMIN_ONLY])
async def get_admin_endpoint(
    fin_kod: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    return await get_admin(fin_kod, db)


@router.put("/admins/{fin_kod}", dependencies=[ADMIN_ONLY])
async def update_admin_endpoint(
    payload: UpdateAdmin,
    fin_kod: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    return await update_admin(fin_kod, payload, db)


@router.delete("/admins/{fin_kod}")
async def delete_admin_endpoint(
    request: Request,
    fin_kod: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current=Depends(token_required(allowed_roles=[1])),
):
    return await delete_admin(fin_kod, db, current_fin_kod=current.get("fin_kod"))
