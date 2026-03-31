import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

import httpx

from app.exceptions import BookNotFoundException, ExchangeRateApiException
from app.models.book import PriceCalculationResponse
from app.repositories.book_repository import BookRepository

EXCHANGE_RATE_API_URL = os.getenv(
    "EXCHANGE_RATE_API_URL",
    "https://api.exchangerate-api.com/v4/latest/USD",
)
TARGET_CURRENCY = os.getenv("TARGET_CURRENCY", "VES")
MARGIN_PERCENTAGE = Decimal("40")


class CalculatePrice:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def execute(self, book_id: int) -> PriceCalculationResponse:
        book = await self.repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(f"Libro con ID {book_id} no encontrado")

        exchange_rate = await self._get_exchange_rate()
        
        # Calculo del pago local, ejemplo: libro 10$, BCV: 500, costo local: 5000
        cost_local = (book.cost_usd * exchange_rate)
        
        # Calculo de venta, el costo local + el 40% de ese costo
        selling_price = (cost_local * (MARGIN_PERCENTAGE / Decimal("100"))) + cost_local
        
        # Actualizo el libro con el precio a vender local
        book.selling_price_local = round(selling_price,2)
        await self.repository.update(book)

        return PriceCalculationResponse(
            book_id=book.id,
            cost_usd=book.cost_usd,
            exchange_rate=exchange_rate,
            cost_local=round(cost_local,2),
            margin_percentage=MARGIN_PERCENTAGE,
            selling_price_local=round(selling_price,2),
            currency=TARGET_CURRENCY,
            calculation_timestamp=datetime.now(),
        )

    async def _get_exchange_rate(self) -> Decimal:
        """Obtiene tasa de cambio. Retorna la tasa o levanta una excepcion."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(EXCHANGE_RATE_API_URL)
                response.raise_for_status()
                data = response.json()
                rates = data.get("rates", {})
                rate = rates.get(TARGET_CURRENCY)
                if rate is None:
                    raise ExchangeRateApiException('Hubo un error al intentar ir a buscar la tasa de cambio en la API.')
                
                return Decimal(str(rate))
                
        except (httpx.HTTPError, Exception):
            raise ExchangeRateApiException('Hubo un error al intentar ir a buscar la tasa de cambio en la API.')
