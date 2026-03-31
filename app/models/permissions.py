import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, Column, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class PermissionType(str, Enum):
    ENDPOINT = "endpoint"
    FRONT = "front"
    NAVIGATION = "navigation"


# ────────────────────────────────────────────────── Modelo DB ───────────────────────────────────────────────
class Permissions(SQLModel, table=True):
    __tablename__ = "permissions"

    id: uuid.UUID = Field(sa_column=Column(UUID, primary_key=True))
    permission_code: str = Field(max_length=255, unique=True, nullable=False)
    functionality: str = Field(max_length=255, nullable=False)
    descripcion: str = Field(sa_column=Column(Text))
    type: str = Field(
        default="endpoint",
        max_length=20,
        sa_column_args=(
            CheckConstraint("type IN ('endpoint', 'front', 'navigation')"),
        ),
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: uuid.UUID = Field(sa_column=Column(UUID))
    updated_by: uuid.UUID = Field(sa_column=Column(UUID))


# ────────────────────────────────────────────────── Schemas API ─────────────────────────────────────────────
class PermissionsCreate(SQLModel):
    permission_code: str = Field(max_length=255)
    functionality: str = Field(max_length=255)
    descripcion: str = Field(sa_column=Column(Text))
    type: PermissionType = Field(default=PermissionType.ENDPOINT)


# class PermissionsResponse(SQLModel):
#     id: uuid.UUID
#     nombre: str
#     descripcion: Optional[str]
#     precio: Decimal
#     stock: int
#     created_at: datetime
#     updated_at: Optional[datetime]
