from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationInfo(BaseModel):
    page: int = Field(default=1, description="Página actual")
    limit: int = Field(default=10, description="Registros por página")
    total_pages: int = Field(default=0, description="Total de páginas")
    total_records: int = Field(default=0, description="Total de registros")
    info: list = Field(default_factory=list, description="Lista de registros")


class APIResponse(BaseModel, Generic[T]):
    success: bool = Field(default=True, description="Indicador de éxito")
    message: str = Field(default="", description="Mensaje descriptivo")
    outcome: list[Any] = Field(default_factory=list, description="Datos de respuesta")
    errors: list[str] = Field(default_factory=list, description="Lista de errores")
