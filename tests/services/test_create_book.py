from decimal import Decimal

import pytest

from app.exceptions import BookAlreadyExistsException, ValidationException
from app.models.book import BookCreate
from app.services.book import BookUseCase


class TestCreateBook:
    @pytest.mark.asyncio
    async def test_crear_libro_exitoso(
        self, service: BookUseCase, book_data: BookCreate
    ):
        book = await service.create.execute(book_data)

        assert book.id is not None
        assert book.title == book_data.title
        assert book.author == book_data.author
        assert book.isbn == book_data.isbn
        assert book.cost_usd == book_data.cost_usd

    @pytest.mark.asyncio
    async def test_crear_libro_isbn_duplicado(
        self, service: BookUseCase, book_data: BookCreate
    ):
        await service.create.execute(book_data)

        with pytest.raises(BookAlreadyExistsException) as exc:
            await service.create.execute(book_data)

        assert "ISBN" in str(exc.value)

    @pytest.mark.asyncio
    async def test_crear_libro_costo_negativo(self, service: BookUseCase):
        data = BookCreate(
            title="Libro Test",
            author="Autor Test",
            isbn="1234567890",
            cost_usd=Decimal("-5.00"),
            stock_quantity=10,
            category="Test",
            supplier_country="VE",
        )

        with pytest.raises(ValidationException) as exc:
            await service.create.execute(data)

        assert "USD" in str(exc.value)

    @pytest.mark.asyncio
    async def test_crear_libro_stock_negativo(self, service: BookUseCase):
        data = BookCreate(
            title="Libro Test",
            author="Autor Test",
            isbn="1234567890",
            cost_usd=Decimal("10.00"),
            stock_quantity=-1,
            category="Test",
            supplier_country="VE",
        )

        with pytest.raises(ValidationException) as exc:
            await service.create.execute(data)

        assert "stock" in str(exc.value).lower()

    @pytest.mark.asyncio
    async def test_crear_libro_isbn_invalido(self, service: BookUseCase):
        data = BookCreate(
            title="Libro Test",
            author="Autor Test",
            isbn="123",
            cost_usd=Decimal("10.00"),
            stock_quantity=5,
            category="Test",
            supplier_country="VE",
        )

        with pytest.raises(ValidationException) as exc:
            await service.create.execute(data)

        assert "ISBN" in str(exc.value)
