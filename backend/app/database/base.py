"""
FeeAssist AI — SQLAlchemy Declarative Base

All models must import Base from here so Alembic can
discover them through metadata.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
