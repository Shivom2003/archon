"""Async SQLAlchemy engine, session factory, and declarative base."""

import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.settings import settings


def _build_engine():
    """
    Build the async engine with settings appropriate for the host.

    Neon (and most hosted Postgres providers) require SSL.
    We detect this from the URL and pass ssl via connect_args rather than
    as a URL parameter, which is more reliable with asyncpg.

    Pool sizes are kept small because:
    - Neon free tier: 100 max connections
    - Render free tier: 512 MB RAM
    """
    url = settings.database_url
    connect_args: dict = {}

    # Strip ssl/sslmode params from URL — we handle SSL via connect_args instead
    needs_ssl = any(kw in url for kw in ("neon.tech", "ssl=require", "sslmode=require"))
    for param in ("?ssl=require", "&ssl=require", "?sslmode=require", "&sslmode=require"):
        url = url.replace(param, "")

    if needs_ssl:
        ctx = ssl.create_default_context()
        connect_args["ssl"] = ctx

    return create_async_engine(
        url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=5,       # Keep low — Neon free tier caps at 100 total connections
        max_overflow=5,
        connect_args=connect_args,
    )


engine = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
