import os
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    # Anchor relative SQLite paths to the backend project root so the DB
    # file is always the same regardless of where uvicorn was started from.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if "///./" in DATABASE_URL:
        rel = DATABASE_URL.split("///./", 1)[1]
        abs_path = os.path.join(project_root, rel)
        DATABASE_URL = DATABASE_URL.split("///./", 1)[0] + "///" + abs_path

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )
else:
    import ssl
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(DATABASE_URL)
    query_params = parse_qs(parsed.query)
    query_params.pop("sslmode", None)
    query_params.pop("channel_binding", None)
    new_query = urlencode(query_params, doseq=True)
    clean_url = urlunparse(parsed._replace(query=new_query))

    async_database_url = clean_url.replace("postgresql://", "postgresql+asyncpg://")

    ssl_context = ssl.create_default_context()

    engine = create_async_engine(
        async_database_url,
        connect_args={"ssl": ssl_context},
        echo=False,
        future=True,
    )

AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()
