from decimal import Decimal
from uuid import uuid4

from app.models.permissions import ProductoCreate
from app.repositories.permissions_repository import PermissionsRepository


class TestProductoRepository:
    def test_create_producto(
        self,
        repo: PermissionsRepository,
        producto_data: ProductoCreate,
    ):
        producto = repo.create(producto_data)

        assert producto.nombre == producto_data.nombre
        assert producto.descripcion == producto_data.descripcion
        assert producto.precio == producto_data.precio
        assert producto.stock == producto_data.stock
        assert producto.id is not None

    def test_get_by_id_existente(
        self,
        repo: PermissionsRepository,
        producto_data: ProductoCreate,
    ):
        producto_creado = repo.create(producto_data)

        producto = repo.get_by_id(producto_creado.id)

        assert producto is not None
        assert producto.id == producto_creado.id
        assert producto.nombre == producto_data.nombre

    def test_get_by_id_inexistente(self, repo: PermissionsRepository):
        producto = repo.get_by_id(uuid4())

        assert producto is None

    def test_get_all_vacio(self, repo: PermissionsRepository):
        productos = repo.get_all()

        assert productos == []

    def test_get_all_con_datos(
        self,
        repo: PermissionsRepository,
        producto_data: ProductoCreate,
    ):
        repo.create(producto_data)

        productos = repo.get_all()

        assert len(productos) == 1
        assert productos[0].nombre == producto_data.nombre

    def test_get_all_con_paginacion(self, repo: PermissionsRepository):
        for i in range(5):
            data = ProductoCreate(
                nombre=f"Producto {i}",
                precio=Decimal("10.00"),
                stock=1,
            )
            repo.create(data)

        productos = repo.get_all(skip=0, limit=3)

        assert len(productos) == 3

    def test_get_all_con_skip(self, repo: PermissionsRepository):
        for i in range(5):
            data = ProductoCreate(
                nombre=f"Producto {i}",
                precio=Decimal("10.00"),
                stock=1,
            )
            repo.create(data)

        productos = repo.get_all(skip=2, limit=10)

        assert len(productos) == 3

    def test_delete_existente(
        self,
        repo: PermissionsRepository,
        producto_data: ProductoCreate,
    ):
        producto_creado = repo.create(producto_data)

        resultado = repo.delete(producto_creado.id)

        assert resultado is True

        producto = repo.get_by_id(producto_creado.id)
        assert producto is None

    def test_delete_inexistente(self, repo: PermissionsRepository):
        resultado = repo.delete(uuid4())

        assert resultado is False
