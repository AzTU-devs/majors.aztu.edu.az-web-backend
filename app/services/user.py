from typing import Dict, Any
from app.models.user import User
from app.db.session import get_db
from fastapi import status, Depends
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.api.v1.schemas.user import UpdateUser
from sqlalchemy.ext.asyncio import AsyncSession

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