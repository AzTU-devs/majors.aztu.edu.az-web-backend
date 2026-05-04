import os
import jwt
import logging
import datetime
# from app.models. import User
from fastapi import Request, HTTPException


SECRET_KEY = os.getenv('SECRET_KEY')

def encode_auth_token(fin_kod, role, approved):
    try:
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        payload = {
            'fin_kod': fin_kod,
            'role': role,
            'approved': approved,
            'exp': expiration_time
        }

        auth_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return auth_token

    except Exception as e:
        logging.getLogger(__name__).error(f"Error encoding token: {e}")
        return str(e)
    

def decode_auth_token(auth_token):
    try:
        logging.getLogger(__name__).debug(f"Decoding token: {auth_token}")

        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=['HS256'], options={"require": ["exp"]})

        logging.getLogger(__name__).debug(f"Decoded payload: {payload}")

        return {
            'fin_kod': payload['fin_kod'],
            'role': payload['role'],
            'approved': payload['approved'],
        }

    except jwt.ExpiredSignatureError:
        logging.getLogger(__name__).warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logging.getLogger(__name__).warning(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logging.getLogger(__name__).error(f"Error decoding token: {e}")
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

        auth_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return auth_token

    except Exception as e:
        logging.getLogger(__name__).error(f"Error encoding token: {e}")
        return str(e)
    

def decode_otp_token(otp_token):
    try:
        logging.getLogger(__name__).debug(f"Decoding token: {otp_token}")

        payload = jwt.decode(otp_token, SECRET_KEY, algorithms=['HS256'], options={"require": ["exp"]})

        logging.getLogger(__name__).debug(f"Decoded payload: {payload}")

        return {
            'fin_kod': payload['fin_kod'],
            'email': payload['email'],
            'otp': payload['otp'],
        }

    except jwt.ExpiredSignatureError:
        logging.getLogger(__name__).warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logging.getLogger(__name__).warning(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logging.getLogger(__name__).error(f"Error decoding token: {e}")
        raise HTTPException(status_code=500, detail="Error decoding token")

def token_required(allowed_roles=None):
    async def dependency(request: Request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise HTTPException(status_code=401, detail='Authorization token is missing.')

        try:
            token = auth_header.split(" ")[1]
            payload = decode_auth_token(token)

            if payload is None:
                raise HTTPException(status_code=403, detail='Token is invalid or expired.')

            if allowed_roles and payload.get('role') not in allowed_roles:
                raise HTTPException(status_code=403, detail='Access denied: role not allowed.')

            request.state.user = payload
            return payload

        except IndexError:
            raise HTTPException(status_code=403, detail='Invalid token format.')
        except Exception as e:
            raise HTTPException(status_code=403, detail=f'Invalid token: {str(e)}')

    return dependency