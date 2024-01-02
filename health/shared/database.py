from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import current_timestamp
from sqlmodel import Field, SQLModel

from health.core import settings

engine = create_engine(settings.DATABASE_URL, pool_recycle=360, pool_size=20)
engine_with_serializable = create_engine(
    settings.DATABASE_URL,
    pool_recycle=360,
    pool_size=20,
    isolation_level="SERIALIZABLE",
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
SessionSerializable = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine_with_serializable,
)


@contextmanager
def session_scope(is_serializable=False):
    # global session_count
    session = SessionSerializable() if is_serializable else SessionLocal()
    # session_count += 1

    # logging.warning("session_count %d", session_count)

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        # session_count -= 1
        session.close()


class Base(SQLModel):
    id: int = Field(primary_key=True)
    is_deleted: bool = Field(nullable=False, default=0)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        nullable=False,
        sa_column_kwargs={'server_default': text('CURRENT_TIMESTAMP')},
        index=True,
    )
