from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions import BookNotFoundException, ExchangeRateApiException
from app.services.book import BookUseCase


class TestCalculatePrice:
    @pytest.mark.asyncio
    async def test_calcular_precio_exitoso(self, service: BookUseCase, book_data):
        created = await service.create.execute(data=book_data)

        mock_response = AsyncMock()
        mock_response.json = MagicMock(return_value={"rates": {"VES": 36.50}})
        mock_response.raise_for_status = AsyncMock()

        with patch(
            "app.services.book.calculate_price.httpx.AsyncClient.get",
            return_value=mock_response,
        ):
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
    async def test_calcular_precio_api_falla(self, service: BookUseCase, book_data):
        created = await service.create.execute(data=book_data)

        with pytest.raises(ExchangeRateApiException):
            with patch(
                "app.services.book.calculate_price.httpx.AsyncClient.get",
                side_effect=Exception("Connection error"),
            ):
                await service.calculate_price.execute(created.id)
