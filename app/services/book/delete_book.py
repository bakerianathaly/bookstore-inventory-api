from app.exceptions import BookNotFoundException
from app.repositories.book_repository import BookRepository


class DeleteBook:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def execute(self, book_id: int) -> bool:
        book = await self.repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(f"El libro con el ID {book_id} ya ha sido eliminado o no existe")
        
        deleted_book = await self.repository.delete(book)
        return deleted_book
