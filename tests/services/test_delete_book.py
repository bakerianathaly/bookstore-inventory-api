import pytest

from app.exceptions import BookNotFoundException
from app.services.book import BookUseCase


class TestDeleteBook:
    @pytest.mark.asyncio
    async def test_eliminar_libro_exitoso(self, service: BookUseCase, book_data):
        created = await service.create.execute(data=book_data)
        result = await service.delete.execute(created.id)

        assert result is True

        with pytest.raises(BookNotFoundException):
            await service.get.obtener(created.id)

    @pytest.mark.asyncio
    async def test_eliminar_libro_no_existe(self, service: BookUseCase):
        with pytest.raises(BookNotFoundException):
            await service.delete.execute(9999)
