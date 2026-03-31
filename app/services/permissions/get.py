from uuid import UUID

from app.models.api_response import PaginationInfo
from app.models.permissions import Permissions
from app.repositories.permissions_repository import PermissionsRepository


class LeerProducto:
    def __init__(self, repository: PermissionsRepository):
        self.repository = repository

    async def listar(self, is_active: str, page: int = 1, limit: int = 10) -> dict:

        permissions, total_records = await self.repository.get_all_paginated(
            page=page, limit=limit, is_active=is_active
        )
        total_pages = (total_records + limit - 1) // limit if total_records > 0 else 0

        return PaginationInfo(
            page=page,
            limit=limit,
            total_pages=total_pages,
            total_records=total_records,
            info=permissions,
        )

    async def obtener(self, permission_id: UUID) -> Permissions | None:
        return await self.repository.get_by_id(permission_id)
