from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field
from sqlalchemy import text


class TimeMixin(object):
    __abstract__ = True

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": text("now()")}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"onupdate": datetime.now(timezone.utc)}
    )


class AuthorizerMixin(object):
    __abstract__ = True

    created_by: str = Field(default="admin")
    updated_by: str = Field(default="admin")


class SoftDeleteMixin(object):
    __abstract__ = True

    is_deleted: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": text("false")}
    )