from sqlalchemy import or_
from app.utils.otp import *
from app.utils.email import *
from app.models.otp import Otp
from app.models.user import User
from app.utils.security import *
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from app.utils.jwt import encode_otp_token
from fastapi.templating import Jinja2Templates
from app.api.v1.schemas.otp import ValidateOtp
from sqlalchemy.ext.asyncio import AsyncSession

templates = Jinja2Templates(directory="templates")


# Send otp to the user's email using user's fin kod
# Used email util for sending html content
# OTP expiration time is 5 minutes

async def send_otp(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        query_result = await db.execute(
            select(User)
            .where(User.fin_kod == fin_kod)
        )

        user = query_result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Fin kod is not valid."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        otp_query = await db.execute(
            select(Otp)
            .where(Otp.fin_kod == fin_kod)
        )

        previous_otp = otp_query.scalar_one_or_none()

        if previous_otp:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "Otp already exists."
                }, status_code=status.HTTP_409_CONFLICT
            )
        
        otp = await generateOtp()

        hashed_otp = hash_password(otp)

        new_otp = Otp(
            fin_kod=fin_kod,
            otp=hashed_otp,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )

        db.add(new_otp)
        await db.commit()
        await db.refresh(new_otp)
        
        subject = "OTP"

        html_content = templates.get_template("/email/otp_verification.html").render({
            "name": user.name,
            "otp_code": otp
        })

        send_html_email(subject, user.email, user.name, html_content)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "OTP sent successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Validate otp by getting fin kod and otp from user
# Verify otp by verify_password() util
# Return token if the otp verified

async def validate_otp(
    otp_request: ValidateOtp,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        query_result = await db.execute(
            select(User)
            .where(User.fin_kod == otp_request.fin_kod)
        )

        user = query_result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Fin kod is not valid."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        otp_query = await db.execute(
            select(Otp)
            .where(
                Otp.fin_kod == otp_request.fin_kod
            )
        )

        user_otp = otp_query.scalar_one_or_none()

        if not user_otp or not verify_password(str(otp_request.otp), user_otp.otp):
            return JSONResponse(
                content={
                    "status_code": 401,
                    "message": "OTP is invalid or expired."
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if user_otp.expires_at < datetime.utcnow():
            return JSONResponse(
                content={
                    "status_code": 401,
                    "message": "OTP has expired."
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        token = encode_otp_token(otp_request.fin_kod, otp_request.otp)

        await db.delete(user_otp)
        await db.commit()
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Otp validated successfully.",
                "token": token
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )