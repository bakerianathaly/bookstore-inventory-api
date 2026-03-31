import uuid
from app.models.permissions import Permissions, PermissionsCreate
from app.repositories.permissions_repository import PermissionsRepository


class CreatePremissions:
    def __init__(self, repository: PermissionsRepository):
        self.repository = repository

    async def execute(self, permission_data: PermissionsCreate) -> Permissions:
        # Validacion para saber si el nombre del permiso ya existe en BD
        chekc_permission_name = await self.repository.get_permissions_by_code(
            code=permission_data.permission_code
        )
        if chekc_permission_name is not None:
            raise ValueError(
                f"Ya existe un permiso creado con el código {permission_data.permission_code}"
            )

        permission_info = Permissions(
            id=uuid.uuid4(),
            permission_code=permission_data.permission_code,
            functionality=permission_data.functionality.strip().capitalize(),
            descripcion=permission_data.descripcion,
            type=permission_data.type.value,
            created_by=uuid.uuid4(),
            updated_by=uuid.uuid4(),
        )

        nuevo_permiso = await self.repository.create(permission_info)
        return nuevo_permiso
