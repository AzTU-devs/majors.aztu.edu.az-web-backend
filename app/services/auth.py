import logging
import secrets
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, status, HTTPException
from app.models.otp import Otp
from app.models.auth import Auth
from app.db.session import get_db
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from app.utils.email import send_html_email
from app.utils.jwt import encode_auth_token
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.password_validator import validate_password
from app.utils.security import hash_password, verify_password
from app.api.v1.schemas.auth import SignUp, SignIn, ValidateOTP


logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="template")


def _internal_error() -> JSONResponse:
    return JSONResponse(
        content={"statusCode": 500, "message": "Internal server error"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

def generateOtp(length: int = 6) -> str:
    otp = ''.join(str(secrets.randbelow(10)) for _ in range(length))
    return otp

async def signup(
    user: SignUp,
    db: AsyncSession = Depends(get_db)
):
    try:
        from app.models.user import User

        fetched_exist_user = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == user.fin_kod)
        )

        exist_user = fetched_exist_user.scalar_one_or_none()

        if exist_user:
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "Fin kod in use.",
                }, status_code=status.HTTP_409_CONFLICT
            )

        # A profile can only be attached to a free cafedra (unique per user).
        existing_cafedra_user = await db.execute(
            select(User).where(User.cafedra_code == user.cafedra_code)
        )
        if existing_cafedra_user.scalar_one_or_none():
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "Cafedra already has a registered user.",
                }, status_code=status.HTTP_409_CONFLICT
            )

        # validate_password raises HTTPException on weak passwords; surface it as
        # a clean 400 instead of letting the broad handler turn it into a 500.
        try:
            validate_password(user.password)
        except HTTPException as exc:
            return JSONResponse(
                content={"statusCode": exc.status_code, "message": exc.detail},
                status_code=exc.status_code,
            )

        otp = generateOtp()
        hashed_otp = hash_password(otp)
        user_hashed_password = hash_password(user.password)

        new_auth_user = Auth(
            fin_kod = user.fin_kod,
            password = user_hashed_password,
            role = 2,
            approved = False,
            created_at = datetime.utcnow(),
            updated_at = None,
        )

        new_user = User(
            name=user.name,
            surname=user.surname,
            father_name=user.father_name,
            fin_kod=user.fin_kod,
            email=user.email,
            cafedra_code=user.cafedra_code,
            created_at=datetime.utcnow()
        )

        new_otp = Otp(
            fin_kod = user.fin_kod,
            otp = hashed_otp,
            otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
        )

        db.add(new_user)
        db.add(new_auth_user)
        db.add(new_otp)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "User already exists.",
                }, status_code=status.HTTP_409_CONFLICT
            )
        await db.refresh(new_user)
        await db.refresh(new_auth_user)
        await db.refresh(new_otp)

        # Email delivery must never break sign-up; failures are logged inside
        # send_html_email and swallowed here so a mail outage can't 500 register.
        try:
            html_content = templates.get_template("/registration_email.html").render({
                "name": user.name })
            send_html_email("Qeydiyyat", user.email, user.name, html_content)

            html_content = templates.get_template("/otp_verification.html").render({
                "otp_code": otp})
            send_html_email("OTP", user.email, user.name, html_content)
        except Exception:
            logger.exception("Failed to send sign-up emails (non-fatal)")


        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "User temporary saved",
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception:
        logger.exception("Unhandled error in auth service")
        return _internal_error()

async def signin(
    credentials: SignIn,
    db: AsyncSession = Depends(get_db)
):
    try:
        from app.models.user import User

        fetched_exist_user = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == credentials.fin_kod)
        )

        exist_user = fetched_exist_user.scalar_one_or_none()

        if not exist_user:
            return JSONResponse(
                content={
                    "statusCode": 401,
                    "message": "UNAUTHORIZED"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        fetched_user = await db.execute(
            select(User)
            .where(User.fin_kod == credentials.fin_kod)
        )

        user = fetched_user.scalar_one_or_none()
        
        if not verify_password(credentials.password, exist_user.password):
            return JSONResponse(
                content={
                    "statusCode": 401,
                    "message": "UNAUTHORIZED"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )

        if not exist_user.approved:
            return JSONResponse(
                content={
                    "statusCode": 403,
                    "message": "NOT_APPROVED"
                }, status_code=status.HTTP_403_FORBIDDEN
            )

        token = encode_auth_token(exist_user.fin_kod, exist_user.role, exist_user.approved)

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "AUTHORIZED",
                "token": token,
                "user": {
                    "name": user.name,
                    "surname": user.surname,
                    "father_name": user.father_name,
                    "fin_kod": user.fin_kod,
                    "role": exist_user.role,
                    "approved": exist_user.approved,
                    "cafedra_code": user.cafedra_code,
                    "email": user.email,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
            }
        )
    
    except Exception:
        logger.exception("Unhandled error in auth service")
        return _internal_error()

async def validate_otp(
    credentials: ValidateOTP,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == credentials.fin_kod)
        )

        user = result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "User not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        otp_result = await db.execute(
            select(Otp)
            .where(Otp.fin_kod == credentials.fin_kod)
        )

        otp_record = otp_result.scalar_one_or_none()

        if not otp_record:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "OTP not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        if otp_record.otp_expires_at < datetime.utcnow() or not verify_password(credentials.otp, otp_record.otp):
            return JSONResponse(
                content={
                    "statusCode": 401,
                    "message": "Expired otp"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )

        await db.delete(otp_record)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "AUTHORIZED"
            }, status_code=status.HTTP_200_OK
        )
    except Exception:
        logger.exception("Unhandled error in auth service")
        return _internal_error()