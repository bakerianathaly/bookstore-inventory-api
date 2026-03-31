from decimal import Decimal

import pytest

from app.models.permissions import ProductoCreate
from app.services.permissions import PermissionsUseCase


class TestCrearProducto:
    def test_crear_producto_exitoso(
        self,
        service: PermissionsUseCase,
        producto_data: ProductoCreate,
    ):
        producto = service.crear.execute(producto_data)

        assert producto.nombre == producto_data.nombre
        assert producto.descripcion == producto_data.descripcion
        assert producto.precio == producto_data.precio
        assert producto.stock == producto_data.stock
        assert producto.id is not None

    def test_crear_producto_precio_negativo(self, service: PermissionsUseCase):
        data = ProductoCreate(
            nombre="Producto Test",
            precio=Decimal("-5.00"),
            stock=10,
        )

        with pytest.raises(ValueError) as exc:
            service.crear.execute(data)

        assert "precio" in str(exc.value).lower()

    def test_crear_producto_precio_cero(self, service: PermissionsUseCase):
        data = ProductoCreate(
            nombre="Producto Test",
            precio=Decimal("0.00"),
            stock=10,
        )

        with pytest.raises(ValueError) as exc:
            service.crear.execute(data)

        assert "precio" in str(exc.value).lower()

    def test_crear_producto_stock_negativo(self, service: PermissionsUseCase):
        data = ProductoCreate(
            nombre="Producto Test",
            precio=Decimal("100.00"),
            stock=-5,
        )

        with pytest.raises(ValueError) as exc:
            service.crear.execute(data)

        assert "stock" in str(exc.value).lower()

    def test_crear_producto_stock_mayor_10000(self, service: PermissionsUseCase):
        data = ProductoCreate(
            nombre="Producto Test",
            precio=Decimal("100.00"),
            stock=10001,
        )

        with pytest.raises(ValueError) as exc:
            service.crear.execute(data)

        assert "stock" in str(exc.value).lower()

    def test_crear_producto_nombre_menor_3_caracteres(
        self, service: PermissionsUseCase
    ):
        data = ProductoCreate(
            nombre="  AB  ",
            precio=Decimal("100.00"),
            stock=10,
        )

        with pytest.raises(ValueError) as exc:
            service.crear.execute(data)

        assert "nombre" in str(exc.value).lower()

    def test_crear_producto_sin_descripcion(self, service: PermissionsUseCase):
        data = ProductoCreate(
            nombre="Producto Sin Desc",
            precio=Decimal("50.00"),
            stock=5,
        )

        producto = service.crear.execute(data)

        assert producto.nombre == "Producto Sin Desc"
        assert producto.descripcion is None
