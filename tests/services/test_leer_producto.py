from decimal import Decimal

import pytest

from app.models.permissions import ProductoCreate
from app.services.permissions import PermissionsUseCase


class TestLeerProducto:
    def test_listar_productos_vacio(self, service: PermissionsUseCase):
        productos = service.leer.listar()

        assert productos == []

    def test_listar_productos_con_datos(
        self,
        service: PermissionsUseCase,
        producto_data: ProductoCreate,
    ):
        service.crear.execute(producto_data)

        productos = service.leer.listar()

        assert len(productos) == 1
        assert productos[0].nombre == producto_data.nombre

    def test_listar_productos_con_paginacion(
        self,
        service: PermissionsUseCase,
    ):
        for i in range(5):
            data = ProductoCreate(
                nombre=f"Producto {i}",
                precio=Decimal("10.00"),
                stock=1,
            )
            service.crear.execute(data)

        productos = service.leer.listar(skip=0, limit=3)

        assert len(productos) == 3

    def test_listar_productos_paginacion_invalida_skip_negativo(
        self,
        service: PermissionsUseCase,
    ):
        with pytest.raises(ValueError) as exc:
            service.leer.listar(skip=-1)

        assert "skip" in str(exc.value).lower()

    def test_listar_productos_paginacion_invalida_limit_cero(
        self,
        service: PermissionsUseCase,
    ):
        with pytest.raises(ValueError) as exc:
            service.leer.listar(limit=0)

        assert "límite" in str(exc.value).lower()

    def test_listar_productos_paginacion_invalida_limit_mayor_1000(
        self,
        service: PermissionsUseCase,
    ):
        with pytest.raises(ValueError) as exc:
            service.leer.listar(limit=1001)

        assert "límite" in str(exc.value).lower()

    def test_obtener_producto_existente(
        self,
        service: PermissionsUseCase,
        producto_data: ProductoCreate,
    ):
        producto_creado = service.crear.execute(producto_data)

        producto = service.leer.obtener(producto_creado.id)

        assert producto is not None
        assert producto.id == producto_creado.id
        assert producto.nombre == producto_data.nombre

    def test_obtener_producto_inexistente(self, service: PermissionsUseCase):
        from uuid import uuid4

        producto = service.leer.obtener(uuid4())

        assert producto is None
