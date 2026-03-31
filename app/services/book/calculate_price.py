import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

import httpx

from app.exceptions import BookNotFoundException
from app.models.book import PriceCalculationResponse
from app.repositories.book_repository import BookRepository

EXCHANGE_RATE_API_URL = os.getenv(
    "EXCHANGE_RATE_API_URL",
    "https://api.exchangerate-api.com/v4/latest/USD",
)
DEFAULT_EXCHANGE_RATE = Decimal(os.getenv("DEFAULT_EXCHANGE_RATE", "36.50"))
TARGET_CURRENCY = os.getenv("TARGET_CURRENCY", "VES")
MARGIN_PERCENTAGE = Decimal("40")


class CalculatePrice:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def execute(self, book_id: int) -> PriceCalculationResponse:
        book = await self.repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(f"Libro con ID {book_id} no encontrado")

        exchange_rate, is_default = await self._get_exchange_rate()

        cost_local = (book.cost_usd * exchange_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        margin_multiplier = Decimal("1") + (MARGIN_PERCENTAGE / Decimal("100"))
        selling_price = (cost_local * margin_multiplier).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        book.selling_price_local = selling_price
        await self.repository.update(book)

        return PriceCalculationResponse(
            book_id=book.id,
            cost_usd=book.cost_usd,
            exchange_rate=exchange_rate,
            cost_local=cost_local,
            margin_percentage=40,
            selling_price_local=selling_price,
            currency=TARGET_CURRENCY,
            calculation_timestamp=datetime.now(),
        )

    async def _get_exchange_rate(self) -> tuple[Decimal, bool]:
        """Obtiene tasa de cambio. Retorna (tasa, es_default)."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(EXCHANGE_RATE_API_URL)
                response.raise_for_status()
                data = response.json()
                rates = data.get("rates", {})
                rate = rates.get(TARGET_CURRENCY)
                if rate is None:
                    return DEFAULT_EXCHANGE_RATE, True
                return Decimal(str(rate)), False
        except (httpx.HTTPError, Exception):
            return DEFAULT_EXCHANGE_RATE, True
