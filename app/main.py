import os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

CORS_ORIGINS = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()
]
if not CORS_ORIGINS:
    raise ValueError(
        "CORS_ORIGINS environment variable is not set. "
        "Provide a comma-separated list of allowed origins."
    )

from app.api.v1.routes.plo import router as plo_router
# SLO removed from the platform (kept commented for reference).
# from app.api.v1.routes.slo import router as slo_router
from app.api.v1.routes.clo import router as clo_router
from app.api.v1.routes.tlo import router as tlo_router
from app.api.v1.routes.gco import router as gco_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.user import router as user_router
from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.topic import router as topic_router
from app.api.v1.routes.faculty import router as faculty_routes
from app.api.v1.routes.cafedra import router as cafedra_routes
from app.api.v1.routes.specialty import router as specialty_routes
from app.api.v1.routes.competency import router as competency_router
from app.api.v1.routes.university import router as university_routes
from app.api.v1.routes.literature import router as literature_router
from app.api.v1.routes.match import router as match_router
from app.api.v1.routes.clo_plo_match import router as clo_plo_match_router
from app.api.v1.routes.competency_match import router as competency_match_router
from app.api.v1.routes.curricula_program import router as curricula_router
from app.api.v1.routes.specialty_characteristics import router as specialty_characteristics_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=['Auth'])
app.include_router(user_router, prefix="/api", tags=['User'])
app.include_router(admin_router, prefix="/api", tags=['Admin'])
# SLO removed from the platform.
# app.include_router(slo_router, prefix="/api", tags=['SLO'])
app.include_router(plo_router, prefix="/api", tags=['PLO'])
app.include_router(gco_router, prefix="/api", tags=['GCO'])
app.include_router(tlo_router, prefix="/api", tags=['TLO'])
app.include_router(clo_router, prefix="/api", tags=['CLO'])
app.include_router(topic_router, prefix="/api", tags=['TOPIC'])
app.include_router(faculty_routes, prefix="/api", tags=['Faculty'])
app.include_router(cafedra_routes, prefix="/api", tags=['Cafedra'])
app.include_router(specialty_routes, prefix="/api", tags=['Specialty'])
app.include_router(curricula_router, prefix="/api", tags=['Curricula'])
app.include_router(university_routes, prefix="/api", tags=['University'])
app.include_router(competency_router, prefix="/api", tags=['Competency'])
app.include_router(specialty_characteristics_router, prefix="/api", tags=['Specialty_Characteristics'])
app.include_router(literature_router, prefix="/api/literature", tags=['Literature'])
app.include_router(match_router, prefix="/api", tags=['Match'])
app.include_router(clo_plo_match_router, prefix="/api", tags=['CloPloMatch'])
app.include_router(competency_match_router, prefix="/api", tags=['CompetencyMatch'])

@app.on_event("startup")
async def ensure_schema() -> None:
    """Create any newly-added tables and columns so the app is self-migrating.

    ``create_all`` only creates missing tables (checkfirst=True) and the guarded
    ALTER adds the new curricula column when absent. Works for SQLite and Postgres.
    """
    import logging as _logging
    import app.models  # noqa: F401  (registers every model on Base.metadata)
    from sqlalchemy import text
    from app.db.database import Base, engine

    _log = _logging.getLogger(__name__)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Add curricula_program.out_of_class_hours if the table predates it.
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text("ALTER TABLE curricula_program ADD COLUMN out_of_class_hours VARCHAR")
            )
    except Exception:
        # Column already exists (or DB doesn't support the statement) — ignore.
        _log.debug("out_of_class_hours column already present")

    # curricula_program.year is now a free-text academic year ("2025-2026").
    # Convert the legacy INTEGER column to VARCHAR on Postgres; SQLite is
    # dynamically typed and tolerates text in the column, so its ALTER (which it
    # does not support) simply errors and is ignored.
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text("ALTER TABLE curricula_program ALTER COLUMN year TYPE VARCHAR USING year::varchar")
            )
    except Exception:
        _log.debug("curricula_program.year already varchar or not alterable")


@app.get("/")
def read_root():
    return {"message": "API Running"}
