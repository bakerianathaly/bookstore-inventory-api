from uuid import UUID

from app.models.permissions import Permissions
from app.repositories.permissions_repository import PermissionsRepository


class ActualizarProducto:
    def __init__(self, repository: PermissionsRepository):
        self.repository = repository

    async def execute(self, permission_id: UUID, data: dict) -> Permissions | None:
        raise NotImplementedError("Método actualizar no implementado")
