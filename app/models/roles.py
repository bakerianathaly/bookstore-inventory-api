from datetime import datetime
import uuid
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import UUID

# ────────────────────────────────────────────────── Modelo DB ───────────────────────────────────────────────


class Roles(SQLModel, table=True):  # pyright: ignore[reportGeneralTypeIssues, reportCallIssue]
    __tablename__ = "roles"

    id: uuid.UUID = Field(sa_column=Column(UUID, primary_key=True))
    name: str = Field(max_length=255, unique=True, nullable=False)
    profile_id: uuid.UUID = Field(sa_column=Column(UUID))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: uuid.UUID = Field(sa_column=Column(UUID))
    updated_by: uuid.UUID = Field(sa_column=Column(UUID))


class RolesPermissions(SQLModel, table=True):  # pyright: ignore[reportGeneralTypeIssues, reportCallIssue]
    __tablename__ = "role_permissions"

    id: uuid.UUID = Field(sa_column=Column(UUID, primary_key=True))
    role_id: uuid.UUID = Field(foreign_key="roles.id", primary_key=True)
    permissions_id: uuid.UUID = Field(foreign_key="permissions.id", primary_key=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: uuid.UUID = Field(sa_column=Column(UUID))
    updated_by: uuid.UUID = Field(sa_column=Column(UUID))
