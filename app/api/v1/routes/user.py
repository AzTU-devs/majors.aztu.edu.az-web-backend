from typing import Optional
from app.db.session import get_db
from app.utils.jwt import token_required
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.user import ApproveUser
from app.services.user import list_users, set_user_approval, reject_user

router = APIRouter()

# Only the admin / dev role (1) may manage user approvals.
ADMIN_ONLY = Depends(token_required(allowed_roles=[1]))


@router.get("/users", dependencies=[ADMIN_ONLY])
async def list_users_endpoint(
    approved: Optional[bool] = Query(
        default=None,
        description="Filter by approval status. Pass false for pending sign-ups.",
    ),
    db: AsyncSession = Depends(get_db),
):
    return await list_users(db, approved=approved)


@router.post("/users/approve", dependencies=[ADMIN_ONLY])
async def approve_user_endpoint(
    payload: ApproveUser,
    db: AsyncSession = Depends(get_db),
):
    return await set_user_approval(payload.fin_kod, payload.approved, db)


@router.delete("/users/{fin_kod}", dependencies=[ADMIN_ONLY])
async def reject_user_endpoint(
    fin_kod: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    return await reject_user(fin_kod, db)
