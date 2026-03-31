from app.exceptions import BookNotFoundException
from app.repositories.book_repository import BookRepository


class DeleteBook:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def execute(self, book_id: int) -> bool:
        book = await self.repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(f"Libro con ID {book_id} no encontrado")

        return await self.repository.delete(book)
