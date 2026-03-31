from uuid import uuid4

from app.models.permissions import ProductoCreate
from app.services.permissions import PermissionsUseCase


class TestEliminarProducto:
    def test_eliminar_producto_existente(
        self,
        service: PermissionsUseCase,
        producto_data: ProductoCreate,
    ):
        producto_creado = service.crear.execute(producto_data)

        resultado = service.eliminar.execute(producto_creado.id)

        assert resultado is True

        producto = service.leer.obtener(producto_creado.id)
        assert producto is None

    def test_eliminar_producto_inexistente(self, service: PermissionsUseCase):
        resultado = service.eliminar.execute(uuid4())

        assert resultado is False
