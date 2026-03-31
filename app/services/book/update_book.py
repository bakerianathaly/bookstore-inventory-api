from app.exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    ValidationException,
)
from app.models.book import (
    Book,
    BookUpdate,
    validate_cost_usd,
    validate_isbn,
    validate_stock,
)
from app.repositories.book_repository import BookRepository


class UpdateBook:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def execute(self, book_id: int, data: BookUpdate) -> Book:
        book = await self.repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(f"Libro con ID {book_id} no encontrado")

        self._validar(data, book.isbn)

        update_data = data.model_dump(exclude_unset=True)

        if "isbn" in update_data:
            existing = await self.repository.get_by_isbn(update_data["isbn"])
            if existing is not None and existing.id != book_id:
                raise BookAlreadyExistsException(
                    f"Ya existe un libro con ISBN {update_data['isbn']}"
                )

        for key, value in update_data.items():
            setattr(book, key, value)

        return await self.repository.update(book)

    def _validar(self, data: BookUpdate, current_isbn: str) -> None:
        if data.isbn is not None:
            if not validate_isbn(data.isbn):
                raise ValidationException("ISBN inválido: debe tener 10 o 13 dígitos")
        if data.cost_usd is not None:
            if not validate_cost_usd(data.cost_usd):
                raise ValidationException("El costo en USD debe ser mayor a 0")
        if data.stock_quantity is not None:
            if not validate_stock(data.stock_quantity):
                raise ValidationException("La cantidad en stock no puede ser negativa")
