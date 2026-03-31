import re
from app.exceptions import BookAlreadyExistsException, ValidationException
from app.models.book import Book, BookCreate
from app.repositories.book_repository import BookRepository


class CreateBook:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def validate_isbn(self, isbn: str) -> bool:
        """Valida formato ISBN-10 o ISBN-13 (con o sin guiones)."""
        clean = isbn.replace("-", "").replace(" ", "")
        return bool(re.match(r"^(\d{10}|\d{13})$", clean))

    async def execute(self, *, data: BookCreate) -> Book:

        # Valido si ya existe un libro por su ISBN
        existing = await self.repository.get_by_isbn(data.isbn)
        if existing is not None:
            raise BookAlreadyExistsException(f"Ya existe un libro con ISBN {data.isbn}")

        # Extra: Valido si ya existe un libro por ese nombre, en sagas siempre se pone el nombre + numero de libro
        existing = await self.repository.get_by_title(data.title)
        if existing is not None:
            raise BookAlreadyExistsException(
                f"Ya existe un libro con el nombre {data.title}"
            )

        # Validacion del formato del ISBN
        if not self.validate_isbn(data.isbn):
            raise ValidationException("ISBN inválido: debe tener 10 o 13 dígitos")

        # Validacion del costo del libro sea mayor que 0
        if data.cost_usd <= 0:
            raise ValidationException("El costo en USD debe ser mayor a 0")

        # Validacion del inventario del libro no sea menor que 0
        if not data.stock_quantity < 0:
            raise ValidationException("La cantidad en stock no puede ser negativa")

        # Creacion del objeto para crear el libro
        book = Book(
            title=data.title,
            author=data.author,
            isbn=data.isbn,
            cost_usd=data.cost_usd,
            stock_quantity=data.stock_quantity,
            category=data.category,
            supplier_country=data.supplier_country,
        )

        # Creacion del libro
        new_book = await self.repository.create(book)

        return new_book
