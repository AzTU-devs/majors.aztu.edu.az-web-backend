import logging
from typing import Dict, Any, Optional
from app.models.otp import Otp
from app.models.auth import Auth
from app.models.user import User
from app.db.session import get_db
from fastapi import status, Depends
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.api.v1.schemas.user import UpdateUser
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def list_users(
    db: AsyncSession,
    approved: Optional[bool] = None,
):
    """List users joined with their auth record.

    When ``approved`` is provided, only users whose auth.approved matches are
    returned (e.g. ``approved=False`` → pending sign-ups awaiting approval).
    """
    try:
        query = select(User, Auth).join(Auth, Auth.fin_kod == User.fin_kod)
        if approved is not None:
            query = query.where(Auth.approved == approved)
        query = query.order_by(Auth.created_at.desc())

        result = await db.execute(query)
        rows = result.all()

        users = [
            {
                "fin_kod": user.fin_kod,
                "name": user.name,
                "surname": user.surname,
                "father_name": user.father_name,
                "email": user.email,
                "cafedra_code": user.cafedra_code,
                "role": auth.role,
                "approved": auth.approved,
                "created_at": auth.created_at.isoformat() if auth.created_at else None,
            }
            for user, auth in rows
        ]

        return JSONResponse(
            content={"statusCode": 200, "users": users},
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error in list_users")
        return JSONResponse(
            content={"statusCode": 500, "message": "Internal server error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def set_user_approval(
    fin_kod: str,
    approved: bool,
    db: AsyncSession,
):
    """Approve (or revoke approval for) a user's auth record."""
    try:
        result = await db.execute(select(Auth).where(Auth.fin_kod == fin_kod))
        auth = result.scalar_one_or_none()

        if not auth:
            return JSONResponse(
                content={"statusCode": 404, "message": "User not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        auth.approved = approved
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "User approved." if approved else "User approval revoked.",
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        await db.rollback()
        logger.exception("Error in set_user_approval")
        return JSONResponse(
            content={"statusCode": 500, "message": "Internal server error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def reject_user(
    fin_kod: str,
    db: AsyncSession,
):
    """Reject a pending sign-up by removing its otp, user and auth records."""
    try:
        auth_result = await db.execute(select(Auth).where(Auth.fin_kod == fin_kod))
        auth = auth_result.scalar_one_or_none()
        if not auth:
            return JSONResponse(
                content={"statusCode": 404, "message": "User not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        otp_result = await db.execute(select(Otp).where(Otp.fin_kod == fin_kod))
        otp = otp_result.scalar_one_or_none()
        if otp:
            await db.delete(otp)

        user_result = await db.execute(select(User).where(User.fin_kod == fin_kod))
        user = user_result.scalar_one_or_none()
        if user:
            await db.delete(user)

        await db.delete(auth)
        await db.commit()

        return JSONResponse(
            content={"statusCode": 200, "message": "User rejected and removed."},
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        await db.rollback()
        logger.exception("Error in reject_user")
        return JSONResponse(
            content={"statusCode": 500, "message": "Internal server error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

async def patch_user(
    update_data: UpdateUser,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        result = await db.execute(select(User).where(User.fin_kod == update_data.fin_kod))
        user = result.scalar_one_or_none()

        if not user:
            raise JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "User not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        update_dict: Dict[str, Any] = update_data.dict(exclude_unset=True)

        for key, value in update_dict.items():
            if key != "fin_kod":
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "User updated successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        await db.rollback()
        raise JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }
        )

async def delete_user(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(User)
            .where(User.fin_kod == fin_kod)
        )

        user = result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "User not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        await db.delete(user)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "User deleted succesfully"
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        raise JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )