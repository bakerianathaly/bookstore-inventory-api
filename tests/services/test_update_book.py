from decimal import Decimal

import pytest

from app.exceptions import BookNotFoundException, ValidationException
from app.models.book import BookUpdate
from app.services.book import BookUseCase


class TestUpdateBook:
    @pytest.mark.asyncio
    async def test_actualizar_titulo(self, service: BookUseCase, book_data):
        created = await service.create.execute(data=book_data)
        data = BookUpdate(title="Nuevo Título")

        updated = await service.update.execute(created.id, data)

        assert updated.title == "Nuevo Título"
        assert updated.author == created.author

    @pytest.mark.asyncio
    async def test_actualizar_precio(self, service: BookUseCase, book_data):
        created = await service.create.execute(data=book_data)
        data = BookUpdate(cost_usd=Decimal("25.00"))

        updated = await service.update.execute(created.id, data)

        assert updated.cost_usd == Decimal("25.00")

    @pytest.mark.asyncio
    async def test_actualizar_libro_no_existe(self, service: BookUseCase):
        data = BookUpdate(title="Test")

        with pytest.raises(BookNotFoundException):
            await service.update.execute(9999, data)

    @pytest.mark.asyncio
    async def test_actualizar_precio_negativo(self, service: BookUseCase, book_data):
        created = await service.create.execute(data=book_data)
        data = BookUpdate(cost_usd=Decimal("-10.00"))

        with pytest.raises(ValidationException):
            await service.update.execute(created.id, data)

    @pytest.mark.asyncio
    async def test_actualizar_stock_negativo(self, service: BookUseCase, book_data):
        created = await service.create.execute(data=book_data)
        data = BookUpdate(stock_quantity=-5)

        with pytest.raises(ValidationException):
            await service.update.execute(created.id, data)
