from app.repositories.permissions_repository import PermissionsRepository
from app.services.permissions.actualizar_producto import ActualizarProducto
from app.services.permissions.create import CreatePremissions
from app.services.permissions.eliminar_producto import EliminarProducto
from app.services.permissions.get import LeerProducto


class PermissionsUseCase:
    def __init__(self, repository: PermissionsRepository):
        self.create_new_permissions = CreatePremissions(repository)
        self.leer = LeerProducto(repository)
        self.actualizar = ActualizarProducto(repository)
        self.eliminar = EliminarProducto(repository)
