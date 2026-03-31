import re
from app.exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    ValidationException,
)
from app.models.book import Book, BookUpdate
from app.repositories.book_repository import BookRepository


class UpdateBook:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def validate_isbn(self, isbn: str) -> bool:
        """Valida formato ISBN-10 o ISBN-13 (con o sin guiones)."""
        clean = isbn.replace("-", "").replace(" ", "")
        return bool(re.match(r"^(\d{10}|\d{13})$", clean))

    async def execute(self, book_id: int, data: BookUpdate) -> Book:
        book = await self.repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(f"Libro con ID {book_id} no encontrado")

        # Valido si ya existe un libro por su ISBN
        if data.isbn is not None:
            existing = await self.repository.get_by_isbn(data.isbn)
            if existing is not None:
                raise BookAlreadyExistsException(
                    f"Ya existe un libro con ISBN {data.isbn}"
                )

            # Validacion del formato del ISBN
            if not self.validate_isbn(data.isbn):
                raise ValidationException("ISBN inválido: debe tener 10 o 13 dígitos")

        # Extra: Valido si ya existe un libro por ese nombre, en sagas siempre se pone el nombre + numero de libro
        if data.title is not None:
            existing = await self.repository.get_by_title(data.title)
            if existing is not None:
                raise BookAlreadyExistsException(
                    f"Ya existe un libro con el nombre {data.title}"
                )

        # Validacion del costo del libro sea mayor que 0
        if data.cost_usd is not None:
            if data.cost_usd <= 0:
                raise ValidationException("El costo en USD debe ser mayor a 0")

        # Validacion del inventario del libro no sea menor que 0
        if data.stock_quantity is not None:
            if data.stock_quantity < 0:
                raise ValidationException("La cantidad en stock no puede ser negativa")

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(book, key, value)

        book_updated = await self.repository.update(book)
        return book_updated
