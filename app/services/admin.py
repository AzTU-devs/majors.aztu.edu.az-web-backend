import logging
from datetime import datetime
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import Auth
from app.models.admin_profile import AdminProfile
from app.utils.security import hash_password
from app.utils.password_validator import validate_password
from app.api.v1.schemas.admin import CreateAdmin, UpdateAdmin

logger = logging.getLogger(__name__)

ADMIN_ROLE = 1


def _internal_error() -> JSONResponse:
    return JSONResponse(
        content={"statusCode": 500, "message": "Internal server error"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def create_admin(payload: CreateAdmin, db: AsyncSession):
    """Create an admin/dev account (auth.role == 1, approved) + its profile.

    Also self-heals partial states: if an admin auth row exists but is missing
    its profile (e.g. the seeded admin, or a half-finished create), the profile
    is attached instead of hard-failing. Each conflict returns a specific reason
    so the caller never sees a vague "already exists".
    """
    try:
        existing_auth = (
            await db.execute(select(Auth).where(Auth.fin_kod == payload.fin_kod))
        ).scalar_one_or_none()

        # FIN already belongs to a NON-admin (e.g. a kafedra müdiri) account.
        if existing_auth and existing_auth.role != ADMIN_ROLE:
            return JSONResponse(
                content={"statusCode": 409, "message": "Fin kod in use by a non-admin account."},
                status_code=status.HTTP_409_CONFLICT,
            )

        # Email is unique across admin profiles (ignore the row we may complete).
        email_owner = (
            await db.execute(select(AdminProfile).where(AdminProfile.email == payload.email))
        ).scalar_one_or_none()
        if email_owner and email_owner.fin_kod != payload.fin_kod:
            return JSONResponse(
                content={"statusCode": 409, "message": "Email already in use."},
                status_code=status.HTTP_409_CONFLICT,
            )

        existing_profile = (
            await db.execute(select(AdminProfile).where(AdminProfile.fin_kod == payload.fin_kod))
        ).scalar_one_or_none()

        # A fully-formed admin already exists — nothing to do.
        if existing_auth and existing_profile:
            return JSONResponse(
                content={"statusCode": 409, "message": "An admin with this FIN already exists."},
                status_code=status.HTTP_409_CONFLICT,
            )

        now = datetime.utcnow()

        if existing_auth is None:
            # Brand-new admin: validate password and create the auth row.
            try:
                validate_password(payload.password)
            except HTTPException as exc:
                return JSONResponse(
                    content={"statusCode": exc.status_code, "message": exc.detail},
                    status_code=exc.status_code,
                )
            db.add(Auth(
                fin_kod=payload.fin_kod,
                password=hash_password(payload.password),
                role=ADMIN_ROLE,
                approved=True,
                created_at=now,
                updated_at=None,
            ))
        # else: existing admin auth without a profile -> just attach the profile
        # (its existing password is kept, so this can't hijack a live account).

        db.add(AdminProfile(
            fin_kod=payload.fin_kod,
            name=payload.name,
            surname=payload.surname,
            email=payload.email,
            created_at=now,
        ))

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return JSONResponse(
                content={"statusCode": 409, "message": "Admin already exists."},
                status_code=status.HTTP_409_CONFLICT,
            )

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": (
                    "Admin created."
                    if existing_auth is None
                    else "Admin profile attached to the existing account."
                ),
            },
            status_code=status.HTTP_201_CREATED,
        )
    except Exception:
        await db.rollback()
        logger.exception("Error in create_admin")
        return _internal_error()


async def list_admins(db: AsyncSession):
    """List every admin/dev account with its profile (if any)."""
    try:
        result = await db.execute(
            select(Auth, AdminProfile)
            .outerjoin(AdminProfile, AdminProfile.fin_kod == Auth.fin_kod)
            .where(Auth.role == ADMIN_ROLE)
            .order_by(Auth.created_at.desc())
        )
        rows = result.all()

        admins = [
            {
                "fin_kod": auth.fin_kod,
                "name": profile.name if profile else None,
                "surname": profile.surname if profile else None,
                "email": profile.email if profile else None,
                "role": auth.role,
                "approved": auth.approved,
                "created_at": auth.created_at.isoformat() if auth.created_at else None,
            }
            for auth, profile in rows
        ]

        return JSONResponse(
            content={"statusCode": 200, "admins": admins},
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error in list_admins")
        return _internal_error()


async def get_admin(fin_kod: str, db: AsyncSession):
    try:
        result = await db.execute(
            select(Auth, AdminProfile)
            .outerjoin(AdminProfile, AdminProfile.fin_kod == Auth.fin_kod)
            .where(Auth.fin_kod == fin_kod, Auth.role == ADMIN_ROLE)
        )
        row = result.first()
        if not row:
            return JSONResponse(
                content={"statusCode": 404, "message": "Admin not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        auth, profile = row
        return JSONResponse(
            content={
                "statusCode": 200,
                "admin": {
                    "fin_kod": auth.fin_kod,
                    "name": profile.name if profile else None,
                    "surname": profile.surname if profile else None,
                    "email": profile.email if profile else None,
                    "role": auth.role,
                    "approved": auth.approved,
                    "created_at": auth.created_at.isoformat() if auth.created_at else None,
                },
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error in get_admin")
        return _internal_error()


async def update_admin(fin_kod: str, payload: UpdateAdmin, db: AsyncSession):
    try:
        auth_result = await db.execute(
            select(Auth).where(Auth.fin_kod == fin_kod, Auth.role == ADMIN_ROLE)
        )
        auth = auth_result.scalar_one_or_none()
        if not auth:
            return JSONResponse(
                content={"statusCode": 404, "message": "Admin not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if payload.password is not None:
            try:
                validate_password(payload.password)
            except HTTPException as exc:
                return JSONResponse(
                    content={"statusCode": exc.status_code, "message": exc.detail},
                    status_code=exc.status_code,
                )
            auth.password = hash_password(payload.password)

        if payload.approved is not None:
            auth.approved = payload.approved

        profile_result = await db.execute(
            select(AdminProfile).where(AdminProfile.fin_kod == fin_kod)
        )
        profile = profile_result.scalar_one_or_none()

        if profile is None:
            # Only materialize a profile when the caller actually supplies the
            # full profile details. A password/approval-only update must not
            # create a blank one (empty, and empty email collides on the
            # unique constraint for a second profile-less admin).
            if (
                payload.name is not None
                and payload.surname is not None
                and payload.email is not None
            ):
                profile = AdminProfile(
                    fin_kod=fin_kod,
                    name=payload.name,
                    surname=payload.surname,
                    email=payload.email,
                    created_at=datetime.utcnow(),
                )
                db.add(profile)
        else:
            if payload.name is not None:
                profile.name = payload.name
            if payload.surname is not None:
                profile.surname = payload.surname
            if payload.email is not None:
                profile.email = payload.email
            profile.updated_at = datetime.utcnow()

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return JSONResponse(
                content={"statusCode": 409, "message": "Email already in use."},
                status_code=status.HTTP_409_CONFLICT,
            )

        return JSONResponse(
            content={"statusCode": 200, "message": "Admin updated."},
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        await db.rollback()
        logger.exception("Error in update_admin")
        return _internal_error()


async def delete_admin(fin_kod: str, db: AsyncSession, current_fin_kod: str = None):
    try:
        auth_result = await db.execute(
            select(Auth).where(Auth.fin_kod == fin_kod, Auth.role == ADMIN_ROLE)
        )
        auth = auth_result.scalar_one_or_none()
        if not auth:
            return JSONResponse(
                content={"statusCode": 404, "message": "Admin not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if current_fin_kod is not None and current_fin_kod == fin_kod:
            return JSONResponse(
                content={"statusCode": 400, "message": "You cannot delete your own account."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        profile_result = await db.execute(
            select(AdminProfile).where(AdminProfile.fin_kod == fin_kod)
        )
        profile = profile_result.scalar_one_or_none()
        if profile:
            await db.delete(profile)

        await db.delete(auth)
        await db.commit()

        return JSONResponse(
            content={"statusCode": 200, "message": "Admin deleted."},
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        await db.rollback()
        logger.exception("Error in delete_admin")
        return _internal_error()
