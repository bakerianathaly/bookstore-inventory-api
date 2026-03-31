from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from app.exceptions import BookNotFoundException
from app.services.book import BookUseCase


class TestCalculatePrice:
    @pytest.mark.asyncio
    async def test_calcular_precio_exitoso(self, service: BookUseCase, book_data):
        created = await service.create.execute(book_data)

        mock_response = AsyncMock()
        mock_response.json.return_value = {"rates": {"VES": 36.50}}
        mock_response.raise_for_status = AsyncMock()

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await service.calculate_price.execute(created.id)

        assert result.book_id == created.id
        assert result.cost_usd == Decimal("15.99")
        assert result.exchange_rate == Decimal("36.50")
        assert result.margin_percentage == 40
        assert result.currency == "VES"
        assert result.selling_price_local > result.cost_local

    @pytest.mark.asyncio
    async def test_calcular_precio_libro_no_existe(self, service: BookUseCase):
        with pytest.raises(BookNotFoundException):
            await service.calculate_price.execute(9999)

    @pytest.mark.asyncio
    async def test_calcular_precio_api_falla_usa_default(
        self, service: BookUseCase, book_data
    ):
        created = await service.create.execute(book_data)

        with patch("httpx.AsyncClient.get", side_effect=Exception("Connection error")):
            result = await service.calculate_price.execute(created.id)

        assert result.exchange_rate == Decimal("36.50")
        assert result.selling_price_local > 0
        assert result.currency == "VES"
