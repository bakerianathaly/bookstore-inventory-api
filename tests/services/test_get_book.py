import pytest

from app.exceptions import BookNotFoundException
from app.services.book import BookUseCase


class TestGetBook:
    @pytest.mark.asyncio
    async def test_obtener_libro_por_id(self, service: BookUseCase, book_data):
        created = await service.create.execute(book_data)
        found = await service.get.obtener(created.id)

        assert found.id == created.id
        assert found.title == created.title

    @pytest.mark.asyncio
    async def test_obtener_libro_no_existe(self, service: BookUseCase):
        with pytest.raises(BookNotFoundException):
            await service.get.obtener(9999)

    @pytest.mark.asyncio
    async def test_listar_libros_paginado(
        self, service: BookUseCase, book_data, book_data_2
    ):
        await service.create.execute(book_data)
        await service.create.execute(book_data_2)

        result = await service.get.listar(page=1, limit=10)

        assert result.total_records == 2
        assert len(result.info) == 2
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_buscar_por_categoria(
        self, service: BookUseCase, book_data, book_data_2
    ):
        await service.create.execute(book_data)
        await service.create.execute(book_data_2)

        result = await service.get.buscar_por_categoria("Clásica")

        assert result.total_records == 2
        assert len(result.info) == 2

    @pytest.mark.asyncio
    async def test_libros_bajo_stock(
        self, service: BookUseCase, book_data, book_data_2
    ):
        await service.create.execute(book_data)
        await service.create.execute(book_data_2)

        result = await service.get.bajo_stock(threshold=10)

        assert result.total_records == 1
        assert result.info[0]["stock_quantity"] < 10
