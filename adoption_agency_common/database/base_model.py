from datetime import datetime
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, declarative_base, mapped_column

# class Base(DeclarativeBase):
#     """The central registry and metadata container for all ORM models."""
#     pass
__Base = declarative_base()


class BaseModel(__Base):
    """
    An abstract base class so actual tables inherit 
    common columns automatically without duplicating code.
    """
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())