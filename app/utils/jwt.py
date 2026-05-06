import os
import jwt
import logging
import datetime
from fastapi import Request, HTTPException


SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )

logger = logging.getLogger(__name__)


def encode_auth_token(fin_kod, role, approved):
    try:
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        payload = {
            'fin_kod': fin_kod,
            'role': role,
            'approved': approved,
            'exp': expiration_time
        }

        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    except Exception as e:
        logger.exception("Error encoding auth token")
        raise HTTPException(status_code=500, detail="Token encoding failed") from e


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(
            auth_token, SECRET_KEY, algorithms=['HS256'], options={"require": ["exp"]}
        )
        return {
            'fin_kod': payload['fin_kod'],
            'role': payload['role'],
            'approved': payload['approved'],
        }

    except jwt.ExpiredSignatureError:
        logger.info("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        logger.info("Invalid token presented")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        logger.exception("Error decoding auth token")
        raise HTTPException(status_code=500, detail="Error decoding token")


def encode_otp_token(fin_kod, email, otp):
    try:
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=3)

        payload = {
            'fin_kod': fin_kod,
            'email': email,
            'otp': otp,
            'exp': expiration_time
        }

        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    except Exception as e:
        logger.exception("Error encoding OTP token")
        raise HTTPException(status_code=500, detail="OTP token encoding failed") from e


def decode_otp_token(otp_token):
    try:
        payload = jwt.decode(
            otp_token, SECRET_KEY, algorithms=['HS256'], options={"require": ["exp"]}
        )
        return {
            'fin_kod': payload['fin_kod'],
            'email': payload['email'],
            'otp': payload['otp'],
        }

    except jwt.ExpiredSignatureError:
        logger.info("OTP token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        logger.info("Invalid OTP token presented")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        logger.exception("Error decoding OTP token")
        raise HTTPException(status_code=500, detail="Error decoding token")


def token_required(allowed_roles=None):
    async def dependency(request: Request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail='Authorization token is missing.')

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            raise HTTPException(status_code=401, detail='Authorization token is missing.')

        payload = decode_auth_token(token)

        if allowed_roles and payload.get('role') not in allowed_roles:
            raise HTTPException(status_code=403, detail='Access denied: role not allowed.')

        request.state.user = payload
        return payload

    return dependency
