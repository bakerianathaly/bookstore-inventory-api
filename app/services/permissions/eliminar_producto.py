from uuid import UUID

from app.repositories.permissions_repository import PermissionsRepository


class EliminarProducto:
    def __init__(self, repository: PermissionsRepository):
        self.repository = repository

    async def execute(self, permission_id: UUID) -> bool:
        return await self.repository.delete(permission_id)
